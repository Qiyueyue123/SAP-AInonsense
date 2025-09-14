import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import the official scoring engine
from testScoring import ResumeProcessor

# --- Initialization ---
load_dotenv()
try:
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    processor = ResumeProcessor() # Create an instance of our scoring engine
    print("✅ LangChain models and ResumeProcessor initialized for career coach.")
except Exception as e:
    llm = None
    processor = None
    print(f"❌ ERROR initializing models for coach: {e}")

# --- "Tools" the LLM can use ---
@tool
def update_target_vector(user_id: str, skill: str, score: int, db) -> str:
    """Use this tool when a user wants to SET A GOAL or TARGET for a skill."""
    if not db: return "Error: Database connection is not available."
    try:
        user_ref = db.collection('users').document(user_id)
        user_ref.set({'targetVector': {skill: score}}, merge=True)
        return f"Got it! I've set your target for '{skill}' to a score of {score}."
    except Exception as e:
        return f"Error updating your profile: {e}"

@tool
def add_achievement_and_rescore(user_id: str, achievement_description: str, achievement_type: str, db) -> str:
    """
    Use this tool when a user mentions a NEW ACHIEVEMENT, like completing a course or project,
    and wants to UPDATE THEIR SKILL SCORES. The 'achievement_type' must be one of: 
    'courses', 'projects', 'jobs_internships', or 'competitions'.
    """
    if not db: return "Error: Database connection is not available."
    try:
        print(f"-> Tool: add_achievement_and_rescore called for user {user_id}")
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists: return "User profile not found."
        
        user_profile = user_doc.to_dict()
        resume_json = user_profile.get('resumeJson', {})
        
        new_entry = {"name": "New Achievement", "date": "Recently Completed", "description": achievement_description}
        if achievement_type in resume_json and isinstance(resume_json[achievement_type], list):
            resume_json[achievement_type].append(new_entry)
        else:
            resume_json[achievement_type] = [new_entry]
        
        print("   -> Resume JSON updated with new achievement.")
        
        if not processor: return "Scoring engine is not available."
        skill_summary_obj, feedback_str = processor.processResume(resume_json, from_file=False)
        new_skill_scores = skill_summary_obj.to_dict()
        
        print("   -> Re-scoring complete. New scores:", new_skill_scores)

        user_ref.set({
            'resumeJson': resume_json,
            'skillScores': new_skill_scores,
            'qualitativeFeedback': feedback_str
        }, merge=True)
        
        return f"Excellent! I've added your new achievement and recalculated your skills. Your profile is now updated."

    except Exception as e:
        return f"An error occurred while updating your skills: {e}"

# --- Bind tools to the LLM ---
tools = [update_target_vector, add_achievement_and_rescore]
if llm:
    llm_with_tools = llm.bind_tools(tools)
else:
    llm_with_tools = None

# --- Main Chatbot Logic ---
def get_chatbot_response(user_message: str, chat_history: list, user_profile: dict, db=None):
    if not llm_with_tools:
        return {"role": "assistant", "content": "Chatbot model is not initialized."}
    user_id = user_profile.get('uid')

    
    system_prompt = f"""
    You are 'Aura', an expert career coach AI. Your primary job is to understand user intent based on the full context of their profile.
    
    HERE IS THE USER'S FULL PROFILE:
    - Raw Resume Data: {json.dumps(user_profile.get('resumeJson'), indent=2)}
    - Calculated Skill Scores (out of 20): {json.dumps(user_profile.get('skillScores'), indent=2)}
    - Target Goals: {json.dumps(user_profile.get('targetVector'), indent=2)}

    YOUR TASKS:
    - If the user asks a general question about their resume (e.g., "what was my role at X?"), answer it by referencing the 'Raw Resume Data'.
    - If the user talks about a GOAL or TARGET, use the 'update_target_vector' tool.
    - If the user mentions something they HAVE COMPLETED or FINISHED, use the 'add_achievement_and_rescore' tool.
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
                if "user_id" in selected_tool.args: function_args['user_id'] = user_id
                if "db" in selected_tool.args: function_args['db'] = db
                
                tool_output = selected_tool.invoke(function_args)
                return {"role": "assistant", "content": str(tool_output)}
            else:
                return {"role": "assistant", "content": "Sorry, I couldn't find the right tool."}

        return {"role": "assistant", "content": ai_response_msg.content}
    except Exception as e:
        print(f"❌ ERROR during LangChain invocation: {e}")
        return {"role": "assistant", "content": "I'm having trouble processing that request."}


    

