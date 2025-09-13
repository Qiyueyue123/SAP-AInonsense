import json
import os
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.scoring_agent import score_resume

def run_full_pipeline_test():
    """
    Loads a sample PDF resume and runs it through the entire backend
    processing and scoring pipeline, then prints the final results.
    """
    print("--- Full Backend Pipeline Test ---")
    
    # 1. DEFINE THE INPUT FILE
    # Make sure you have a file named "Resume.pdf" in your backend directory.
    sample_resume_path = "Resume.pdf"
    
    if not os.path.exists(sample_resume_path):
        print(f"❌ ERROR: The sample resume '{sample_resume_path}' was not found in the backend directory.")
        return

    print(f"📄 Loading resume: '{sample_resume_path}'...")
    
    try:
        # 2. RUN THE PIPELINE STEPS
        # We open the file in binary read ('rb') mode
        with open(sample_resume_path, 'rb') as pdf_file:
            print("Step 1: Converting PDF to image...")
            base64_image = pdf_page_to_base64(pdf_file)
            print("✅ PDF converted successfully.")

        print("\nStep 2: Processing resume image with Gemini to get structured JSON...")
        # The process_resume function expects the raw base64 string
        resume_json = process_resume(base64_image)
        # In a real scenario, you'd parse this if it's a string, but let's assume it returns a dict/list
        print("✅ Resume processed into JSON successfully.")

        print("\nStep 3: Scoring the structured resume data...")
        # The scoring agent takes the structured JSON from the previous step
        skill_scores, qualitative_feedback = score_resume(resume_json)
        print("✅ Scoring complete.")

        # 3. PRINT THE FINAL RESULTS
        print("\n--- 📊 FINAL RESULTS ---")
        
        print("\nQualitative Feedback:")
        print(f"  Strengths: {qualitative_feedback.get('strengths')}")
        print(f"  Weaknesses: {qualitative_feedback.get('weaknesses')}")
        
        print("\nCalculated Skill Scores (out of 20):")
        # Pretty-print the JSON for readability
        print(json.dumps(skill_scores, indent=2))

    except Exception as e:
        print(f"\n❌ An error occurred during the pipeline: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_full_pipeline_test()
