import json
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
import os
from dotenv import load_dotenv

# --- Initialization (runs once when the module is imported) ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Main Function ---
def score_resume(resume_data):
    """
    Analyzes and scores a resume provided in a structured JSON format from Gemini.
    Returns the final skill scores and qualitative AI feedback.
    """
    # Step 1: Ensure resume_data is a Python list/dict, not a JSON string
    resume_json = None
    if isinstance(resume_data, str):
        try:
            resume_json = json.loads(resume_data)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Failed to parse resume_json string.")
            resume_json = [{"error": "Invalid JSON format received from processing agent."}]
    else:
        resume_json = resume_data

    if not resume_json or not isinstance(resume_json, list):
        print(f"⚠️ Warning: score_resume received invalid data: {resume_json}")
        return {}, {"strengths": "N/A", "weaknesses": "N/A"}

    # --- Scoring Configuration ---
    SKILL_KEYWORDS = {
        'Code Optimization': ['optimized code', 'performance tuning', 'refactored', 'scalable code'],
        'Database Management': ['database', 'sql', 'schema', 'relational db', 'postgresql', 'mysql'],
        'Data Analysis': ['data analysis', 'pandas', 'numpy', 'insights', 'analytics'],
        'UI/UX Design': ['ui', 'ux', 'user interface', 'user experience', 'wireframe', 'figma'],
        'Automation/Scripting': ['automation', 'scripting', 'automated', 'etl', 'workflow'],
        'Communication': ['communication', 'presenting', 'collaboration', 'interpersonal'],
        'Problem Solving': ['problem solving', 'structured thinking', 'analytical thinking', 'troubleshooting'],
        'Client Management': ['client', 'stakeholder', 'presentation to client', 'requirements gathering'],
        'Team Leadership': ['leadership', 'team lead', 'mentored', 'managed team'],
        'Presentation Skills': ['presentation', 'slides', 'pitched', 'powerpoint', 'storytelling']
    }
    
    # Helper functions
    def similarity_score(text, keyword):
        return util.cos_sim(model.encode(text), model.encode(keyword))[0][0].item()

    def ask_gpt(prompt):
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    # --- Data Processing ---
    skillArray = []
    index_counter = 0
    
    # This loop is updated to handle the list of sections from Gemini
    for section in resume_json:
        header = section.get("header", "").lower()
        content = section.get("content", [])
        
        # Map header to a source type for weighting
        source = "jobs_internships" # Default
        if "education" in header: source = "education"
        elif "experience" in header or "work" in header: source = "jobs_internships"
        elif "course" in header: source = "courses"
        elif "competition" in header or "award" in header: source = "competitions"

        for entry in content:
            index_counter += 1
            
            # This is the CORE FIX: Handle both strings and dictionaries for an entry
            full_text = ""
            if isinstance(entry, dict):
                full_text = ' '.join(str(value) for value in entry.values())
            elif isinstance(entry, str):
                full_text = entry
            
            if not full_text: continue

            # Calculate semantic similarity scores for the entry
            skillDict = {}
            for skill, keywords in SKILL_KEYWORDS.items():
                max_score = max(similarity_score(full_text.lower(), kw.lower()) for kw in keywords) if keywords else 0
                if max_score > 0.3:
                    skillDict[skill] = round(max_score, 3)
            
            if skillDict:
                skillArray.append([index_counter, skillDict, source])

    # --- Final Scoring (Weights and Caps) ---
    source_weights = {"education": 1.5, "jobs_internships": 2.0, "courses": 0.5, "competitions": 0.8}
    source_caps = {"education": 8, "jobs_internships": 10, "courses": 4, "competitions": 4}
    skill_scores = {skill: 0 for skill in SKILL_KEYWORDS}
    skill_breakdown = {skill: {source: 0 for source in source_weights} for skill in SKILL_KEYWORDS}

    for _, skill_dict, source in skillArray:
        weight = source_weights.get(source, 0)
        cap = source_caps.get(source, 0)
        for skill, raw_score in skill_dict.items():
            if skill not in skill_scores: continue
            weighted_score = raw_score * weight
            current_source_score = skill_breakdown[skill].get(source, 0)
            allowable_addition = min(weighted_score, cap - current_source_score)
            if allowable_addition > 0:
                skill_breakdown[skill][source] += allowable_addition
                skill_scores[skill] += allowable_addition

    final_scores = {skill: min(round(score, 3), 20) for skill, score in skill_scores.items()}

    # --- Get Qualitative Feedback ---
    feedback_prompt = f"""
    You are a career advisor AI. Based on the following skill scores (out of 20), provide one concise sentence for strengths and one for weaknesses. Return a JSON object with two keys: "strengths" and "weaknesses".

    Skill Scores: {json.dumps(final_scores)}
    """
    feedback_response_str = ask_gpt(feedback_prompt)
    try:
        qualitative_feedback = json.loads(feedback_response_str.strip().replace("`", ""))
    except json.JSONDecodeError:
        qualitative_feedback = {"strengths": "Analysis incomplete.", "weaknesses": "Could not parse AI feedback."}

    return final_scores, qualitative_feedback

