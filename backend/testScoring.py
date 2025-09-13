## To test the scoring system based on a fake resume
import json
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
import os
from dotenv import load_dotenv
load_dotenv()


# Load and parse labeled resume text
filename = 'testResume.json'
resume = None
with open(filename, 'r', encoding='utf-8') as f:
    raw = f.read()
    print("File size:", os.path.getsize("testResume.json"))
    try:
        resume = json.loads(raw)
        print("JSON loaded successfully!")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")

# Skill keywords
SKILL_KEYWORDS = {
    'Code Optimization': [
        'optimized code', 'performance tuning', 'refactored', 'scalable code',
        'profiling', 'memory management', 'runtime improvement', 'reduced complexity', 'improved efficiency'
    ],
    'Database Management': [
        'database', 'sql', 'schema', 'relational db', 'postgresql', 'mysql',
        'data modeling', 'queries', 'joins', 'stored procedures', 'indexing', 'oracle', 'mongodb'
    ],
    'Data Analysis': [
        'data analysis', 'pandas', 'numpy', 'insights', 'analytics', 'statistics', 'visualization',
        'data wrangling', 'data cleaning', 'trend analysis', 'exploratory analysis', 'data-driven'
    ],
    'UI/UX Design': [
        'ui', 'ux', 'user interface', 'user experience', 'wireframe', 'figma',
        'prototyping', 'design thinking', 'mockups', 'accessibility', 'interaction design'
    ],
    'Automation/Scripting': [
        'automation', 'scripting', 'automated', 'etl', 'workflow',
        'bash', 'shell script', 'automation tools', 'task scheduler', 'cron jobs'
    ],
    'Communication': [
        'communication', 'presenting', 'spoken', 'written',
        'collaboration', 'interpersonal', 'public speaking', 'team communication', 'report writing'
    ],
    'Problem Solving': [
        'problem solving', 'structured thinking', 'framework',
        'analytical thinking', 'troubleshooting', 'root cause analysis', 'strategic thinking'
    ],
    'Client Management': [
        'client', 'stakeholder', 'presentation to client',
        'account management', 'stakeholder communication', 'client engagement', 'requirements gathering'
    ],
    'Team Leadership': [
        'leadership', 'team lead', 'mentored', 'managed team',
        'supervised', 'delegated tasks', 'led project', 'team coordination', 'project management'
    ],
    'Presentation Skills': [
        'presentation', 'slides', 'deck', 'pitched', 'powerpoint',
        'keynote', 'storytelling', 'visual communication', 'demoed', 'delivered presentation'
    ]
}

# Flatten skill names
target_skills = list(SKILL_KEYWORDS.keys())

# Initialize sentence-transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Helper function: semantic similarity
def similarity_score(text, keyword):
    return util.cos_sim(model.encode(text), model.encode(keyword))[0][0].item()

# Helper function: OpenAI call
#api_key=os.getenv("SECRET_KEY")
client = OpenAI()

def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# Student class
class StudentSkill:
    def __init__(self):
        self.skills = {skill: 0 for skill in target_skills}
    def update_skill(self, skill, score):
        if skill in self.skills: 
            self.skills[skill] = max(self.skills[skill], score)
    def __repr__(self):
        return json.dumps(self.skills, indent=2)

# Create student object
returnStudentSkill = StudentSkill()

skillArray = []

if(resume):
    # Step 1: Loop through resume and build skillArray and queryBuffer
    queryBuffer = []
    index = 0
    for achievementType, entries in resume.items():
        for entry in entries:
            index += 1
            full_text = ' '.join(str(value) for value in entry.values())

            # Calculate similarity scores for each skill
            skillDict = {}
            for skill, keywords in SKILL_KEYWORDS.items():
                max_score = 0
                for keyword in keywords:
                    score = similarity_score(full_text.lower(), keyword.lower())
                    if score > max_score:
                        max_score = score
                if max_score > 0.3:  # threshold to reduce noise
                    skillDict[skill] = round(max_score, 3)

            if skillDict:
                skillArray.append([index, skillDict, achievementType])
            
            # Add to queryBuffer
            queryBuffer.append((index, entry, achievementType))

    # Step 2: Ask OpenAI for reputation scores
    reputation_prompt = "Rate the following experiences based on how reputable or well-known they seem. Use a scale from 1 (very obscure) to 5 (globally known). Return JSON list of objects with `reputationScore`, `achievementType`, and `index`. Here are the entries:\n\n"
    for (entry, i, a_type) in queryBuffer:
        reputation_prompt += f"\nEntry {i} ({a_type}): {json.dumps(entry)}\n"

    reputation_response = ask_gpt(reputation_prompt)

    try:
        reputation_list = json.loads(reputation_response)
    except json.JSONDecodeError as e:
        print("Failed to parse OpenAI response:", e)
        reputation_list = []

    # Step 3: Post-process skillArray by multiplying scores with reputation
    for rep in reputation_list:
        rep_index = rep.get("index")
        rep_score = rep.get("reputationScore", 1)

        for skill_entry in skillArray:
            idx, skill_dict, ach_type = skill_entry
            if idx == rep_index:
                # Multiply each skill's score
                for skill in skill_dict:
                    skill_dict[skill] = round(skill_dict[skill] * rep_score, 3)
                break
            #This is really unoptimized but I can't be bothered to do it better

source_weights = {
    "education": 1.5,
    "jobs_internships": 2,
    "courses": 0.5,
    "competitions": 0.8
}

source_caps = {
    "education": 8,
    "jobs_internships": 10,
    "courses": 4,
    "competitions": 4
}
# Initialize score trackers
skill_scores = {skill: 0 for skill in SKILL_KEYWORDS}
skill_breakdown = {skill: {"education": 0, "jobs_internships": 0, "courses": 0, "competitions": 0} for skill in SKILL_KEYWORDS}

# Process each entry in skillArray
for index, skill_dict, source in skillArray:
    weight = source_weights.get(source, 0)
    cap = source_caps.get(source, 0)

    for skill, raw_score in skill_dict.items():
        if skill not in skill_scores:
            continue

        # Calculate weighted score
        weighted_score = raw_score * weight

        # Apply per-source cap per skill
        current = skill_breakdown[skill][source]
        allowable_addition = min(weighted_score, cap - current)

        if allowable_addition > 0:
            skill_breakdown[skill][source] += allowable_addition
            skill_scores[skill] += allowable_addition

# Cap final score at 20 per skill
for skill in skill_scores:
    if skill_scores[skill] > 20:
        skill_scores[skill] = 20

final_result = [{"skill": skill, "score": round(score, 3)} for skill, score in skill_scores.items()]

# Update the student's skill profile with the final skill scores
for skill, score in skill_scores.items():
    returnStudentSkill.update_skill(skill, round(score, 3))

# ---------- OUTPUT ----------

print(skillArray)

print(returnStudentSkill)

feedback_prompt = f"""
You are a career advisor AI. Based on the following skill scores (out of 20), provide one concise sentence highlighting the person's strengths, and one concise sentence highlighting their weaknesses. Be specific and only output two sentences — no bullet points, no extra commentary.

Skill Scores:
{returnStudentSkill}
"""

# Call OpenAI
feedback_response = ask_gpt(feedback_prompt)

# Print result
print(feedback_response)

# Return student object for programmatic use
# first element should be the skillSet updated
# second element is the qualitative feedback
result = [returnStudentSkill, feedback_prompt]