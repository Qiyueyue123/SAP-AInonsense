from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json
import re

# --- Initialization ---
load_dotenv()

def extract_json_from_string(text):
    """
    Finds and parses the first valid JSON object or list from a string.
    Handles markdown code fences (```json ... ```).
    """
    # Regex to find JSON enclosed in ```json ... ``` or just { ... } or [ ... ]
    match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match:
        # If the markdown block is found, use its content. Otherwise, use the raw JSON.
        json_str = match.group(1) if match.group(1) else match.group(2)
        try:
            # Return the parsed JSON object
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️ Warning: Found a JSON-like string but failed to parse.")
            return None
    return None

def process_resume(base64_image):
    """
    Analyzes a resume image using a Google Gemini model via LangChain.
    """
    print('process resume reached')
    
    try:
        model = init_chat_model("gemini-1.5-flash", model_provider="google_genai", temperature=0)
    except Exception as e:
        print(f"❌ ERROR initializing Gemini model: {e}")
        return {"error": "Failed to initialize the AI model. Check credentials."}

    query = """
    Please analyze the resume image and split it into its respective sections. For each section, return the following:
    1. A header (the title of the section).
    2. Content or a list of entries within that section.
    The output must be a valid JSON list where each section is a JSON object with "header" and "content" keys. Do not include any text or markdown formatting outside of the JSON list itself.
    """
    message = HumanMessage(
        content=[
            {"type": "text", "text": query},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ],
    )
    
    try:
        print("...Calling Gemini model to analyze resume...")
        response = model.invoke([message])
        raw_content = response.content
        print("✅ Gemini model call successful.")
        
        # Use the new helper function to clean and parse the response
        parsed_json = extract_json_from_string(raw_content)
        
        if not parsed_json:
            print("❌ ERROR: Could not extract valid JSON from Gemini's response.")
            return {"error": "Failed to parse the AI model's response."}
        
        response_data = parsed_json

    except Exception as e:
        print(f"❌ ERROR during Gemini model invocation: {e}")
        response_data = {"error": f"AI model failed to process the resume: {e}"}

    print('process resume ended')
    return response_data