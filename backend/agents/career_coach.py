import os
import json
import firebase_admin
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI 
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import OpenAIEmbeddings
from firebase_admin import firestore, credentials
from sklearn.metrics.pairwise import cosine_similarity
import sys

load_dotenv()
rel_path = os.getenv("GEMENI_GOOGLE_CREDENTIALS")

# Resolve it relative to THIS file's directory (agents folder)
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # agents folder
project_root = os.path.join(current_file_dir, "..")  # backend folder
key_path = os.path.abspath(os.path.join(project_root, rel_path))

#FOR TESTING
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

db = firestore.client()

# Add the parent directory (backend/) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from testScoring import ResumeProcessor

# --- Initialization ---

embeddings = OpenAIEmbeddings()

try:
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.6)
    processor = ResumeProcessor() # Create an instance of our scoring engine
    print("✅ LangChain models and ResumeProcessor initialized for career coach.")
except Exception as e:
    llm = None
    processor = None
    print(f"❌ ERROR initializing models for coach: {e}")


#store last 10 messages in firestore for chat history
def store_short_term_memory(user_id, chat_history, db):
    try:
        user_ref = db.collection('user_conversations').document(user_id)
        # Store last 10 messages (or however many you want)
        user_ref.set({
            'chat_history': chat_history[-10:],  # keep last 10 messages
        }, merge=True)
        print("Short-term memory stored!")
    except Exception as e:
        print(f"Error storing short-term memory: {e}")

def retrieve_short_term_memory(user_id, db):
    try:
        # Access the user's conversation history from Firestore
        user_ref = db.collection('user_conversations').document(user_id)
        doc = user_ref.get()
        # If the document exists, return the chat history (last 10 messages)
        if doc.exists:
            user_data = doc.to_dict()
            chat_history = user_data.get('chat_history', [])
            return chat_history
        return []  # If no history is found, return an empty list
    except Exception as e:
        print(f"Error retrieving short-term memory: {e}")
        return []  # Return empty if there's an error


#to store embedding of conversation to firestore as long term memory
def store_long_term_memory(user_id, conversation_summary, db):
    # Generate the embedding for the conversation summary (using OpenAIEmbeddings)
    memory_embedding = embeddings.embed_query(conversation_summary)  # Use embed_query instead of embed
    user_ref = db.collection('users').document(user_id)    

    # Store the memory inside the user's document under a new 'memories' field (without ArrayUnion)
    user_ref.set({
        'memories': firestore.ArrayUnion([{
            'embedding': memory_embedding,
            'summary': conversation_summary
        }]),
        'last_updated': firestore.SERVER_TIMESTAMP  # Timestamp stored separately
    }, merge=True)  # Merge ensures existing fields are not overwritten
    
    print("Long-term memory (summary and embedding) stored!")

def retrieve_relevant_memory(user_id, current_input, db):
    # Generate embedding for the current input (user's new message)
    input_embedding = embeddings.embed(current_input)
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    relevant_memories = []
    if user_doc.exists:
        user_data = user_doc.to_dict()
        memories = user_data.get('memories', [])
        for memory in memories:
            memory_embedding = memory['embedding']
            # Calculate similarity between the current input embedding and past memory embeddings
            similarity = cosine_similarity([input_embedding], [memory_embedding])
            if similarity > 0.7:  # threshold for semantic relevance
                relevant_memories.append(memory['summary'])
    return relevant_memories

# --- "Tools" the LLM can use ---
@tool
def update_target_vector(user_id: str, skill: str, score: int, db) -> str:
    """Use this tool when a user says he wants to change his end goal job or career path."""
    if not db: return "Error: Database connection is not available."
    try:
        user_ref = db.collection('users').document(user_id)
        user_ref.set({'targetVector': {skill: score}}, merge=True)
        # user_ref.update({'careerPath':firestore.ArrayRemove()})
        #FIGURE OUT HOW TO CHANGE CAREER PATH ARRAY
        return f"Got it! I've set your target for '{skill}' to a score of {score}."
    except Exception as e:
        return f"Error updating your profile: {e}"

# --- Bind tools to the LLM ---
tools = [update_target_vector]
if llm:
    llm_with_tools = llm.bind_tools(tools)
else:
    llm_with_tools = None

# --- Main Chatbot Logic ---
def get_chatbot_response(user_message: str, uid: str,  db=None):
    if not llm_with_tools:
        return {"role": "assistant", "content": "Chatbot model is not initialized."}
    short_term_memory = retrieve_short_term_memory(uid, db)
    chat_history = short_term_memory + [{"role": "user", "content": user_message}]
    user_profile = db.collection("users").document(uid).get().to_dict()
    
    system_prompt = f"""
    You are 'Aura', an expert career coach AI. Your primary job is to understand user intent based on the full context of their profile.
    
    HERE IS THE USER'S FULL PROFILE:
    - Raw Resume Data: {json.dumps(user_profile.get('resumeJson'), indent=2)}
    - Calculated Skill Scores (out of 20): {json.dumps(user_profile.get('skillScores'), indent=2)}
    - Target Goals: {json.dumps(user_profile.get('targetVector'), indent=2)}

    YOUR TASKS:
    - If the user asks a general question about their resume (e.g., "what was my role at X?"), answer it by referencing the 'Raw Resume Data'.
    - If the user talks about a desired job or wanting to change their career path, use the 'update_target_vector' tool.
    - For anything else, respond conversationally.
    """
    
    messages = [SystemMessage(content=system_prompt)] + chat_history + [{"role": "user", "content": user_message}]

    try:
        ai_response_msg = llm_with_tools.invoke(messages)
        
        if ai_response_msg.tool_calls:
            tool_call = ai_response_msg.tool_calls[0]
            function_name = tool_call['name']
            function_args = tool_call['args']
            selected_tool = next((t for t in tools if t.name == function_name), None)
            
            if selected_tool:
                if "user_id" in selected_tool.args: function_args['user_id'] = uid
                if "db" in selected_tool.args: function_args['db'] = db
                
                tool_output = selected_tool.invoke(function_args)
                return {"role": "assistant", "content": str(tool_output)}
            else:
                return {"role": "assistant", "content": "Sorry, I couldn't find the right tool."}

        conversation_summary = ai_response_msg.content
        store_long_term_memory(uid, conversation_summary, db)  # Save to Firestore

        # Store the last 10 messages as short-term memory in Firestore
        store_short_term_memory(uid, chat_history, db)
        
        return {"role": "assistant", "content": ai_response_msg.content}
    except Exception as e:
        print(f"❌ ERROR during LangChain invocation: {e}")
        return {"role": "assistant", "content": "I'm having trouble processing that request."}


    
while True:
    prompt = input("PROMPT: ")
    if prompt == "quit":
        print("exited")
        break
    response = get_chatbot_response(prompt, "z6XyZQLnu9QjwhVAms39PhQSlqP2", db )
    print(response)