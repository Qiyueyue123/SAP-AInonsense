import json
import os
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.scoring_agent import score_resume
from agents.career_coach import get_chatbot_response

def run_end_to_end_test():
    """
    Runs the full pipeline on a sample resume, then starts an interactive
    chat session using the real, calculated scores from that resume.
    """
    print("--- 🏁 End-to-End Backend Test ---")
    
    # --- Part 1: Run the Data Processing Pipeline ---
    sample_resume_path = "Resume.pdf"
    if not os.path.exists(sample_resume_path):
        print(f"❌ ERROR: Sample resume '{sample_resume_path}' not found.")
        return

    print(f"📄 Loading and processing '{sample_resume_path}'...")
    try:
        with open(sample_resume_path, 'rb') as pdf_file:
            base64_image = pdf_page_to_base64(pdf_file)
        resume_json = process_resume(base64_image)
        skill_scores, qualitative_feedback = score_resume(resume_json)
        print("✅ Resume processed and scored successfully.")
    except Exception as e:
        print(f"\n❌ An error occurred during the pipeline: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- Part 2: Prepare for Chat Session ---
    # Create the user profile with the REAL data from the pipeline
    live_user_profile = {
        "skillScores": skill_scores,
        "qualitativeFeedback": qualitative_feedback,
        "targetVector": {} # Start with an empty target vector
    }

    print("\n--- 🤖 Starting Interactive Chat Session ---")
    print("The chatbot is now using the scores calculated from your resume.")
    print("Type 'exit' to end the session.")
    print("-" * 40)

    chat_history = []
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'exit':
            print("Ending chat session.")
            break

        chat_history.append({"role": "user", "content": user_message})

        print("\nCoach is thinking...")
        # Pass the live_user_profile with real data to the chatbot
        ai_response, _ = get_chatbot_response(user_message, chat_history, live_user_profile)

        if not isinstance(ai_response, dict):
            print("\nCoach: [ERROR] The AI agent returned an invalid response.")
            chat_history.append({"role": "assistant", "content": "[AGENT ERROR]"})
            continue

        response_content = ai_response.get('content', "Sorry, I couldn't generate a response.")
        print(f"\nCoach: {response_content}")
        chat_history.append(ai_response)

if __name__ == '__main__':
    run_end_to_end_test()