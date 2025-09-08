## To test the scoring system based on a fake resume
import json
import openai
from sentence_transformers import SentenceTransformer, util
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")

# Load and parse labeled resume text
filename = 'testResume.json'
with open(filename, 'r', encoding='utf-8') as f:
    raw = f.read()
    print(f"Raw file content:\n{raw[:200]}",repr(raw))  # print first 200 chars
    print("File size:", os.path.getsize("testResume.json"))
    try:
        resume = json.loads(raw)
        print("JSON loaded successfully!")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")

# Skill keywords
SKILL_KEYWORDS = {
    'Code Optimization': ['optimized code', 'performance tuning', 'refactored', 'scalable code'],
    'Database Management': ['database', 'sql', 'schema', 'relational db', 'postgresql', 'mysql'],
    'Data Analysis': ['data analysis', 'pandas', 'numpy', 'insights', 'analytics'],
    'UI/UX Design': ['ui', 'ux', 'user interface', 'user experience', 'wireframe', 'figma'],
    'Automation/Scripting': ['automation', 'scripting', 'automated', 'etl', 'workflow'],
    'Communication': ['communication', 'presenting', 'spoken', 'written'],
    'Problem Solving': ['problem solving', 'structured thinking', 'framework'],
    'Client Management': ['client', 'stakeholder', 'presentation to client'],
    'Team Leadership': ['leadership', 'team lead', 'mentored', 'managed team'],
    'Presentation Skills': ['presentation', 'slides', 'deck', 'pitched', 'powerpoint']
}

# Flatten skill names
target_skills = list(SKILL_KEYWORDS.keys())

# Initialize sentence-transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Helper function: semantic similarity
def similarity_score(text, keyword):
    return util.cos_sim(model.encode(text), model.encode(keyword))[0][0].item()

# Helper function: OpenAI call
def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response['choices'][0]['message']['content']

# Student class
class Student:
    def __init__(self):
        self.skills = {skill: 0 for skill in target_skills}

    def update_skill(self, skill, score):
        if skill in self.skills:
            self.skills[skill] = max(self.skills[skill], score)

    def __repr__(self):
        return json.dumps(self.skills, indent=2)

# Create student object
student = Student()

# ---------- EDUCATION ----------
for edu in resume.get('education', []):
    prompt = f"""
    Rate the prestige of the university '{edu['institution']}' on a scale of 1 to 5 (1 = local, 5 = top-tier global), 
    and the relevance of the degree '{edu['degree']}' to skills like coding, databases, communication, leadership, analytics.
    Respond as: Prestige: X, Relevance: Y
    """
    try:
        gpt_response = ask_gpt(prompt)
        prestige = float(gpt_response.split("Prestige:")[1].split(",")[0].strip())
        relevance = float(gpt_response.split("Relevance:")[1].strip())
    except:
        prestige = relevance = 3

    for skill in target_skills:
        score = round(0.7 * relevance + 0.3 * prestige)
        student.update_skill(skill, score)

# ---------- COURSES ----------
for course in resume.get('courses', []):
    text = f"{course['name']} from {course['provider']}".lower()
    for skill, keywords in SKILL_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                student.update_skill(skill, 3)

# ---------- INTERNSHIPS / JOBS ----------
for job in resume.get('jobs_internships', []):
    desc = job['description'].lower()
    prompt = f"""
    Evaluate the company '{job['company']}' on a scale of 1-5 in terms of tier (1 = unknown, 5 = top global),
    and how relevant the role '{job['title']}' is to skills like coding, scripting, data analysis, communication, leadership.
    Description: {desc}
    Respond as: Tier: X, Relevance: Y
    """
    try:
        gpt_response = ask_gpt(prompt)
        tier = float(gpt_response.split("Tier:")[1].split(",")[0].strip())
        relevance = float(gpt_response.split("Relevance:")[1].strip())
    except:
        tier = relevance = 3

    # Check keywords
    for skill, keywords in SKILL_KEYWORDS.items():
        keyword_match = any(kw in desc for kw in keywords)
        sem_score = max([similarity_score(desc, kw) for kw in keywords])
        if keyword_match or sem_score > 0.6:
            score = round(0.6 * relevance + 0.4 * tier)
            student.update_skill(skill, score)

# ---------- COMPETITIONS ----------
for comp in resume.get('competitions', []):
    desc = comp['description'].lower()
    title = comp['title']
    podium = any(x in desc for x in ['1st', '2nd', '3rd', 'first', 'second', 'third'])
    base_score = 4 if podium else 2.5

    prompt = f"""
    Rate the prestige of this competition '{title}' from 1 to 5 (5 = national/global, 1 = local), 
    and how relevant this achievement is to data/tech/consulting skills.
    Description: {desc}
    Respond as: Prestige: X, Relevance: Y
    """
    try:
        gpt_response = ask_gpt(prompt)
        prestige = float(gpt_response.split("Prestige:")[1].split(",")[0].strip())
        relevance = float(gpt_response.split("Relevance:")[1].strip())
    except:
        prestige = relevance = 3

    for skill, keywords in SKILL_KEYWORDS.items():
        keyword_match = any(kw in desc for kw in keywords)
        sem_score = max([similarity_score(desc, kw) for kw in keywords])
        if keyword_match or sem_score > 0.6:
            weight = round(0.4 * prestige + 0.4 * relevance + 0.2 * base_score)
            student.update_skill(skill, weight)

# ---------- OUTPUT ----------
print("\n🎓 Final Student Skill Profile:")
print(student)

# Return student object for programmatic use
result = student