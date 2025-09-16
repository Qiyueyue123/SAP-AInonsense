from langchain.chat_models import init_chat_model
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise ValueError("GEMINI_API_KEY not set in environment")

def edit_resume(header, content, mode, text_rephrase=""):
    print("edit resume reached")

    model = init_chat_model(
        "gemini-2.5-flash",
        model_provider="google_genai",
        temperature=1.2,
        api_key=gemini_key
    )

    # Use SystemMessage and HumanMessage instead of tuples
    chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", '''
         You are an expert career coach guiding the user in writing his/her resume.
         You have two modes:
         1. Paraphrase the input from the user
         2. Help them add a new activity or entry for their resume under the respective section
         
         For both, take context from the section {header} and the details {content}.
         Your job now is mode {mode}.
         
         If mode 1 → rephrase {text_rephrase} and return the paraphrased text.
         If mode 2 → generate JSON for the activity with the following keys:
             "header": section title (e.g. "LEADERSHIP EXPERIENCE | CO-CURRICULAR ACTIVITIES"),
             "content": {{
                "organization": "AIESEC IN NTU",
                "role": "Incoming Global Exchange Team",
                "responsibilities": [
                    "Sourced internships for students from other countries, providing cross-cultural learning opportunities.",
                    "Developed cross-cultural communication skills by collaborating with team members from various countries and working with international partners."
                ],
                "dates": "Aug 2024 - Present"
            }}
         Format responsibilities in CAR style (Challenge, Action, Result).
         '''),
        ("human", "Use mode {mode}, for section {header}, with content {content}, in a professional tone.")
    ]
)

    prompt = chat_template.invoke({
        "mode": mode,
        "header": header,
        "content": content,
        "text_rephrase": text_rephrase
    })

    response = model.invoke(prompt)

    if hasattr(response, "structured_output"):
        response_data = response.structured_output
    else:
        response_data = response.content

    print("edit resume ended")
    return response_data
