from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Get the path from .env
rel_path = os.getenv("GEMENI_GOOGLE_CREDENTIALS")

# Resolve it relative to THIS file's directory (agents folder)
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # agents folder
project_root = os.path.join(current_file_dir, "..")  # backend folder
key_path = os.path.abspath(os.path.join(project_root, rel_path))

print("Using Google credentials at:", key_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

def edit_resume(header, content, mode, text_rephrase = ""): #mode should be 1 or 2 (1 is paraphrase, 2 is add new section)
    print('edit resume reached')
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature=1.2)
    
    chat_template = ChatPromptTemplate.from_messages(
        [
            ("system", '''
             You are an expert career coach guiding the user in writing his/her resume.
        You have two modes:
        1. Paraphrase the input from the user. Omit gibberish or words that do not exists or are completely out of place.
        2. Help them add a new activity or entry for their resume under the respective section
        For both, take context from the section {header} and the details {content}
        Your job now is mode {mode}
        If mode 1, rephrase {text_rephrase} return paraphrased text as output. Do NOT give multiple options, the output is just the string that can replace the given text.
        If mode 2, generate the JSON for the activity based on the context provided. The JSON keys should include
        "header", e.g "LEADERSHIP EXPERIENCE | CO-CURRICULAR ACTIVITIES",
        "content", e.g
        "organization": "AIESEC IN NTU",
        "role": "Incoming Global Exchange Team",
        "responsibilities": [
          "Sourced internships for students from other countries, providing cross-cultural learning opportunities.",
          "Developed cross-cultural communication skills by collaborating with team members from various countries and working with international partners."
        ],
        "dates", eg "Aug 2024 - Present"   
        format the bullet points for the content using the CAR format (Challenge, Action, and Result, highlighting a specific problem, the actions taken to address it, and the outcome achieved.)
             '''),
            ("human", "Use mode {mode}, for a section {header} and content of {content}, using a professional tone")
        ]
    )
    prompt = chat_template.invoke(
        {
            "mode": mode,
            "header" : header,
            "content" : content,
            "text_rephrase" : text_rephrase
        }
    )
    response = model.invoke(prompt)
    # If you're working with LangChain's models, you can specify structured output
    if hasattr(response, 'structured_output'):
        response_data = response.structured_output  # This should already be in JSON-compatible format
    else:
        response_data = response.content
    print('process resume ended')
    return(response_data)


# header = "INTERNSHIP | WORK EXPERIENCE"
# content = "worked at E&Y as an intern, coordinated weekly meetings for group of 20 team members, and worked on a website for the internal audit team"
# text_rephrase = "Supported in refining risk management strategies, creating reports for clients, and staying up to date with industry regulations and best practices."
# response = edit_resume(header, content, "", 2)
# print(response)
