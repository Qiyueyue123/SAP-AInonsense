from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def extract_json_from_string(text):
    """
    Finds and parses the first valid JSON object from a string,
    handling markdown code fences.
    """
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*\})', text)
    if match:
        json_str = match.group(1) if match.group(1) else match.group(2)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️ Warning: Found a JSON-like string but failed to parse.")
            return None
    return None

def process_resume(base64_image):
    print('process resume reached')
    model = init_chat_model("gemini-1.5-flash", model_provider="google_genai", temperature=0)

    # --- THIS PROMPT IS NOW MORE PRECISE ---
    query = """
    Analyze the resume image. Your task is to return a single, valid JSON object.
    The keys of this object MUST be one of the following exact strings: "education", "jobs_internships", "courses", "competitions", "projects".
    The value for each key must be a list of JSON objects, where each object has "name", "date", and "description" keys.
    If a section does not exist in the resume, omit its key entirely from the final object.
    IMPORTANT: Your entire output must be ONLY the JSON object, with no extra text or markdown formatting.
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
        
        parsed_json = extract_json_from_string(raw_content)
        
        if not parsed_json or not isinstance(parsed_json, dict):
            print(f"❌ ERROR: Could not extract a valid JSON dictionary from Gemini's response. Got: {raw_content}")
            return {"error": "Failed to parse the AI model's response into the required dictionary format."}
        
        response_data = parsed_json

    except Exception as e:
        print(f"❌ ERROR during Gemini model invocation: {e}")
        response_data = {"error": f"AI model failed to process the resume: {e}"}

    print('process resume ended')
    return response_data

