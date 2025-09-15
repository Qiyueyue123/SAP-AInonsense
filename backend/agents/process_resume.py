from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GEMENI_GOOGLE_CREDENTIALS")

def process_resume(base64_image):
    print('process resume reached')
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature=0)

    query = """
    Please analyze the resume image and split it into its respective sections. For each section, return the following:
    1. A header (the title of the section).
    2. Content or a list of entries within that section (like job titles, university names, skills, etc.).
    Ensure that the result is dynamic, meaning that if a section does not exist in the resume (like 'Hobbies' or 'Projects'), it is simply omitted.
    The output should be a JSON dictionary where each section contains:
    - "header": the section's title.
    - "content": the content within that section (this could be a list of strings or more detailed information depending on the section).
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
    response = model.invoke([message])

    # Get the response content
    if hasattr(response, 'structured_output'):
        response_data = response.structured_output
    else:
        response_data = response.content
    
    print(f"Raw response: {response_data}")
    print(f"Response type: {type(response_data)}")
    
    # If response_data is already a dict, return it
    if isinstance(response_data, dict):
        print('process resume ended - already dict')
        return response_data
    
    # If it's a string, try to parse it as JSON
    if isinstance(response_data, str):
        try:
            # Remove potential markdown code blocks
            cleaned_response = response_data.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = re.sub(r'^```json\s*', '', cleaned_response)
            if cleaned_response.endswith('```'):
                cleaned_response = re.sub(r'\s*```$', '', cleaned_response)
            
            # Parse the JSON
            parsed_json = json.loads(cleaned_response)
            print('process resume ended - parsed from string')
            return parsed_json
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Problematic content: {response_data}")
            
            # Fallback: return a structured error response
            return {
                "error": "Failed to parse resume",
                "raw_response": str(response_data)[:500]  # Truncate for safety
            }
    
    # If it's neither dict nor string, return error
    print('process resume ended - unexpected type')
    return {
        "error": "Unexpected response type",
        "response_type": str(type(response_data)),
        "raw_response": str(response_data)[:500]
    }