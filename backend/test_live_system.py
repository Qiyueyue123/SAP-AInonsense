import os
import json
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# --- Import your custom agents and classes ---
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.career_coach import get_chatbot_response
# MODIFIED: Import the ResumeProcessor class from your official scoring file
from testScoring import ResumeProcessor 

def run_live_system_test():
    """
    Tests the full backend pipeline with a live Firestore connection,
    using the LangChain-refactored agents and the correct scoring engine.
    """
    print("--- 🏁 Starting Live System Test ---")
    
    # --- Step 1: Initialization ---
    load_dotenv()
    db = None
    try:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        cred = credentials.Certificate(cred_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {"projectId": os.getenv("FIREBASE_PROJECT_ID")})
        db = firestore.client()
        # Instantiate the scoring processor
        processor = ResumeProcessor()
        print("✅ Firebase and agents initialized successfully.")
    except Exception as e:
        print(f"❌ ERROR: Initialization failed: {e}")
        return

    # --- Step 2: Create a Test User and Process Resume ---
    test_user_id = f"test-user-{uuid.uuid4()}"
    user_ref = db.collection('users').document(test_user_id)
    print(f"👤 Created test user with ID: {test_user_id}")

    sample_resume_path = "Resume.pdf"
    if not os.path.exists(sample_resume_path):
        print(f"❌ ERROR: '{sample_resume_path}' not found.")
        return
        
    try:
        print(f"\n📄 Processing '{sample_resume_path}'...")
        with open(sample_resume_path, 'rb') as pdf_file:
            base64_image = pdf_page_to_base64(pdf_file)
        resume_json = process_resume(base64_image)
        # Use the ResumeProcessor instance to score the resume
        skill_summary_obj, feedback_str = processor.processResume(resume_json, from_file=False)
        skill_scores = skill_summary_obj.to_dict()

        # **SAVE TO DATABASE**
        user_ref.set({
            'uid': test_user_id,
            'email': f"{test_user_id}@test.com",
            'resumeJson': resume_json,
            'skillScores': skill_scores,
            'qualitativeFeedback': feedback_str,
            'targetVector': {}
        }, merge=True)
        print("✅ Resume data successfully saved to Firestore.")

    except Exception as e:
        print(f"❌ ERROR during resume processing: {e}")
        import traceback
        traceback.print_exc()
        user_ref.delete()
        return

    # --- Step 3: Interactive Chat Session ---
    print("\n--- 🤖 Starting Interactive Chat Session (LangChain Agent) ---")
    print("The chatbot is now using the scores calculated from your resume.")
    print("Type 'exit' to end.")
    print("-" * 50)
    
    chat_history = []
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'exit':
            print("Ending chat session.")
            user_ref.delete()
            print(f"🧹 Deleted test user {test_user_id} from Firestore.")
            break

        try:
            user_doc = user_ref.get()
            user_profile = user_doc.to_dict()

            print("\nCoach is thinking...")
            ai_response = get_chatbot_response(user_message, chat_history, user_profile, db)
            
            chat_history.append({"role": "user", "content": user_message})
            chat_history.append(ai_response)

            print(f"\nCoach: {ai_response.get('content')}")

            # **VERIFY DATABASE UPDATE**
            if "recalculated" in ai_response.get('content', ''):
                updated_doc = user_ref.get()
                updated_scores = updated_doc.to_dict().get('skillScores')
                print(f"🔍 DB check: Skill scores have been updated -> {updated_scores}")

        except Exception as e:
            print(f"❌ ERROR during chat session: {e}")

if __name__ == '__main__':
    run_live_system_test()

