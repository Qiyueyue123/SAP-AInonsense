import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore

# --- Initialization ---
load_dotenv()
client = None
db = None

try:
    # Initialize OpenAI Client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized successfully.")
    
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        # This part is for standalone testing; app.py handles the main initialization
        print("⚠️ Firebase not initialized. Attempting standalone init for testing...")
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in .env for standalone init.")
        cred = firebase_admin.credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized for standalone testing.")

    db = firestore.client()

except Exception as e:
    print(f"❌ ERROR during initialization in career_coach.py: {e}")


# --- "Tools" the LLM can use ---
# NOTE: These functions now accept a `db` parameter for Firestore access.
def recommend_courses(skill, db=None):
    """Recommends courses for a given skill."""
    # In a real app, this would query a 'courses' collection in Firestore
    dummy_courses = {
        "coding": ["Advanced Python for Data Science", "React Front-End Development"],
        "business": ["Introduction to Marketing Analytics", "Strategic Management 101"],
    }
    return dummy_courses.get(skill.lower(), f"No courses found for {skill}.")

def find_mentor(field, db=None):
    """Finds a mentor in a specific field."""
    # In a real app, this would query a 'mentors' collection in Firestore
    dummy_mentors = {
        "coding": "Jane Doe, Senior Software Engineer at TechCorp.",
        "business": "John Smith, Product Manager at Innovate Inc.",
    }
    return dummy_mentors.get(field.lower(), f"No mentors found for {field}.")
    
def suggest_career_path(user_profile, db=None):
    """Generates a career path suggestion based on the user's full profile."""
    # This function could become a more complex LLM call in the future
    strengths = user_profile.get("qualitativeFeedback", {}).get("strengths", "their existing skills")
    return f"Based on your strengths in {strengths.lower()}, a potential next step could be a 'Junior Business Analyst' role. This would leverage your business acumen while giving you opportunities to grow your technical skills."

def update_target_vector(user_id, skill, score, db=None):
    """Updates the user's target vector in Firestore."""
    if not db:
        return "Database client not available."
    try:
        user_ref = db.collection('users').document(user_id)
        # Use dot notation for updating nested fields
        user_ref.set({'targetVector': {skill: score}}, merge=True)
        return f"Successfully updated target for {skill} to {score}."
    except Exception as e:
        print(f"Error updating target vector in Firestore: {e}")
        return "Failed to update your target vector."

# --- Main Chatbot Logic ---
def get_chatbot_response(user_message, chat_history, user_profile):
    # CRITICAL: Check for initialization errors at the start of the call
    if not client or not db:
        error_message = "OpenAI client is not initialized." if not client else "Firestore client is not initialized."
        print(f"❌ AGENT ERROR: {error_message}")
        return {"role": "assistant", "content": "I'm sorry, there is a configuration error preventing me from working. Please check the server logs."}

    user_id = user_profile.get('user_id', 'test_user') # Get user_id from profile

    tools = [
        {"type": "function", "function": {"name": "recommend_courses", "description": "Get course recommendations for a specific skill (e.g., 'coding', 'business').", "parameters": {"type": "object", "properties": {"skill": {"type": "string", "description": "The skill to find courses for."}}, "required": ["skill"]}}},
        {"type": "function", "function": {"name": "find_mentor", "description": "Find a mentor for a specific field (e.g., 'coding', 'business').", "parameters": {"type": "object", "properties": {"field": {"type": "string", "description": "The field to find a mentor in."}}, "required": ["field"]}}},
        {"type": "function", "function": {"name": "suggest_career_path", "description": "Suggest a career path based on the user's full skill profile.", "parameters": {"type": "object", "properties": {}}}},
        {"type": "function", "function": {"name": "update_target_vector", "description": "Set or update a target skill and score for the user.", "parameters": {"type": "object", "properties": {"skill": {"type": "string", "description": "The name of the skill to update."}, "score": {"type": "number", "description": "The new target score."}}, "required": ["skill", "score"]}}},
    ]

    system_prompt = f"""
    You are 'Aura', an expert career coach AI. Your goal is to help young professionals grow.
    The user's current skill profile is: {json.dumps(user_profile.get('skillScores'), indent=2)}.
    Their target skill vector is: {json.dumps(user_profile.get('targetVector'), indent=2)}.
    Their AI-generated feedback is: {json.dumps(user_profile.get('qualitativeFeedback'), indent=2)}.
    Analyze the user's request. You can either respond directly with a conversational answer or use one of your available tools to get specific information.
    """
    
    messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_message}]

    try:
        print("...Making OpenAI API call...")
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        print("...API call successful.")

        if tool_calls:
            print(f"...Tool call detected: {tool_calls[0].function.name}")
            available_functions = {
                "recommend_courses": recommend_courses, 
                "find_mentor": find_mentor, 
                "suggest_career_path": suggest_career_path,
                "update_target_vector": update_target_vector
            }
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            # Add necessary context to arguments
            if function_name == "suggest_career_path":
                function_args['user_profile'] = user_profile
            if function_name == "update_target_vector":
                function_args['user_id'] = user_id
            
            # Add the db client to all function calls
            function_args['db'] = db
            
            function_response = function_to_call(**function_args)

            # For now, we will just return the direct tool response for clarity in testing.
            # A more advanced version would send this back to the LLM for a natural language summary.
            return {"role": "assistant", "content": f"[Tool Response: {function_name}] {function_response}"}

        # If the model responds directly
        return {"role": "assistant", "content": response_message.content}

    except Exception as e:
        print(f"❌ ERROR during OpenAI API call in agent: {e}")
        return {"role": "assistant", "content": "I'm having trouble processing that request right now. Please try again in a moment."}

