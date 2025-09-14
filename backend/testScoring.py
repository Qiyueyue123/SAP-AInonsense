import json
import os
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class ResumeProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        try:
            self.llm_openai = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0
            )
            print("✅ LangChain OpenAI model initialized for scoring.")
        except Exception as e:
            self.llm_openai = None
            print(f"❌ ERROR initializing LangChain OpenAI model: {e}")
            
        self.SKILL_KEYWORDS = {
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
        self.source_weights = {"education": 1.5, "jobs_internships": 2, "courses": 0.5, "competitions": 0.8, "projects": 0.3}
        self.source_caps = {"education": 8, "jobs_internships": 10, "courses": 4, "competitions": 4, "projects": 4}

    def similarityScore(self, text, keyword):
        return util.cos_sim(self.model.encode(text), self.model.encode(keyword))[0][0].item()

    class StudentSkill:
        def __init__(self, skill_list):
            self.skills = {skill: 0 for skill in skill_list}
        def update_skill(self, skill, score):
            if skill in self.skills: self.skills[skill] = max(self.skills[skill], score)
        def __repr__(self):
            return json.dumps(self.skills, indent=2)
        def to_dict(self):
            return self.skills

    def processResume(self, resume_data, from_file=True):
        resume = None
        if from_file:
            with open(resume_data, 'r', encoding='utf-8') as f:
                resume = json.load(f)
        else:
            resume = resume_data
        if not resume or not isinstance(resume, dict):
            return None, "Error: Invalid resume data."
        
        target_skills = list(self.SKILL_KEYWORDS.keys())
        returnStudentSkill = self.StudentSkill(target_skills)
        skillArray = []
        
        # --- THIS LOOP IS NOW MORE TARGETED AND ROBUST ---
        for achievementType, entries in resume.items():
            if not isinstance(entries, list): continue
            for entry in entries:
                if not isinstance(entry, dict): continue
                
                # FOCUS on the most descriptive fields for more accurate scoring
                name_text = entry.get("name", "")
                desc_text = entry.get("description", "")
                text_to_analyze = f"{name_text}. {desc_text}"

                if not text_to_analyze.strip(): continue

                skillDict = {}
                for skill, keywords in self.SKILL_KEYWORDS.items():
                    max_score = max((self.similarityScore(text_to_analyze.lower(), kw.lower()) for kw in keywords), default=0)
                    # Increased threshold to reduce noise
                    if max_score > 0.45: 
                        skillDict[skill] = round(max_score, 3)
                if skillDict:
                    skillArray.append([0, skillDict, achievementType])
        
        if not skillArray:
            print("⚠️ Warning: No relevant skills found in the resume after processing.")

        # --- The rest of your scoring logic remains the same ---
        skill_scores = {skill: 0 for skill in self.SKILL_KEYWORDS}
        skill_breakdown = {skill: {src: 0 for src in self.source_weights} for skill in self.SKILL_KEYWORDS}
        for _, skill_dict, source in skillArray:
            weight, cap = self.source_weights.get(source, 0), self.source_caps.get(source, 0)
            for skill, raw_score in skill_dict.items():
                if skill not in skill_scores: continue
                weighted_score = raw_score * weight
                current = skill_breakdown[skill].get(source, 0)
                allowable_addition = min(weighted_score, cap - current)
                if allowable_addition > 0:
                    skill_breakdown[skill][source] += allowable_addition
                    skill_scores[skill] += allowable_addition

        for skill in skill_scores:
            skill_scores[skill] = min(skill_scores[skill], 20)
            returnStudentSkill.update_skill(skill, round(skill_scores[skill], 3))

        if not self.llm_openai:
            return returnStudentSkill, "AI feedback model not available."
            
        feedback_prompt = f"Give one concise sentence on strengths and one on weaknesses based on these scores (out of 20):\n{returnStudentSkill}"
        
        response = self.llm_openai.invoke(feedback_prompt)
        feedback_response = response.content

        return returnStudentSkill, feedback_response

