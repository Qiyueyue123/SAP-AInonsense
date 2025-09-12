from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

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
    The output should be a JSON list where each section contains:
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

    # If you're working with LangChain's models, you can specify structured output
    if hasattr(response, 'structured_output'):
        response_data = response.structured_output  # This should already be in JSON-compatible format
    else:
        response_data = response.content
    print('process resume ended')
    return(response_data)