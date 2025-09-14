import json
import os
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


class ResumeProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = OpenAI()
        self.SKILL_KEYWORDS = {
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

        self.source_weights = {
            "education": 1.5,
            "jobs_internships": 2,
            "courses": 0.5,
            "competitions": 0.8,
            "projects":0.3
        }

        self.source_caps = {
            "education": 8,
            "jobs_internships": 10,
            "courses": 4,
            "competitions": 4,
            "projects":4
        }

    def similarityScore(self, text, keyword):
        return util.cos_sim(
            self.model.encode(text),
            self.model.encode(keyword)
        )[0][0].item()

    def askGpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    class StudentSkill:
        def __init__(self, skill_list):
            self.skills = {skill: 0 for skill in skill_list}
        def update_skill(self, skill, score):
            if skill in self.skills:
                self.skills[skill] = max(self.skills[skill], score)
        def __repr__(self):
            return json.dumps(self.skills, indent=2)
        def to_dict(self):
            return self.skills

    def processResume(self, filepath):
        # Load resume
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} not found.")

        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
            try:
                resume = json.loads(raw)
                print("JSON loaded successfully!")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None

        # Process
        target_skills = list(self.SKILL_KEYWORDS.keys())
        returnStudentSkill = self.StudentSkill(target_skills)
        skillArray = []
        queryBuffer = []
        index = 0

        for achievementType, entries in resume.items():
            for entry in entries:
                index += 1
                full_text = ' '.join(str(value) for value in entry.values())

                # Skill matching
                skillDict = {}
                for skill, keywords in self.SKILL_KEYWORDS.items():
                    max_score = 0
                    for keyword in keywords:
                        score = self.similarityScore(full_text.lower(), keyword.lower())
                        if score > max_score:
                            max_score = score
                    if max_score > 0.3:
                        skillDict[skill] = round(max_score, 3)

                if skillDict:
                    skillArray.append([index, skillDict, achievementType])
                queryBuffer.append((index, entry, achievementType))

        # Reputation prompt
        reputation_prompt = "Rate the following experiences based on how reputable or well-known they seem. Use a scale from 1 (very obscure) to 5 (globally known). Return JSON list of objects with `reputationScore`, `achievementType`, and `index`. Here are the entries:\n\n"
        for (i, entry, a_type) in queryBuffer:
            reputation_prompt += f"\nEntry {i} ({a_type}): {json.dumps(entry)}\n"

        reputation_response = self.askGpt(reputation_prompt)

        try:
            reputation_list = json.loads(reputation_response)
        except json.JSONDecodeError as e:
            print("Failed to parse OpenAI response:", e)
            reputation_list = []

        # Multiply scores with reputation
        for rep in reputation_list:
            rep_index = rep.get("index")
            rep_score = rep.get("reputationScore", 1)
            for skill_entry in skillArray:
                idx, skill_dict, ach_type = skill_entry
                if idx == rep_index:
                    for skill in skill_dict:
                        if ach_type != "projects":
                            skill_dict[skill] = round(skill_dict[skill] * rep_score, 3)
                        else:
                            skill_dict[skill] = round(skill_dict[skill] * 2, 3)
                    break

        # Weighted score logic
        skill_scores = {skill: 0 for skill in self.SKILL_KEYWORDS}
        skill_breakdown = {skill: {src: 0 for src in self.source_weights} for skill in self.SKILL_KEYWORDS}

        for index, skill_dict, source in skillArray:
            weight = self.source_weights.get(source, 0)
            cap = self.source_caps.get(source, 0)

            for skill, raw_score in skill_dict.items():
                weighted_score = raw_score * weight
                current = skill_breakdown[skill][source]
                allowable_addition = min(weighted_score, cap - current)
                if allowable_addition > 0:
                    skill_breakdown[skill][source] += allowable_addition
                    skill_scores[skill] += allowable_addition

        # Cap scores at 20
        for skill in skill_scores:
            skill_scores[skill] = min(skill_scores[skill], 20)

        for skill, score in skill_scores.items():
            returnStudentSkill.update_skill(skill, round(score, 3))

        # Feedback prompt
        feedback_prompt = f"""
You are a career advisor AI. Based on the following skill scores (out of 20), provide one concise sentence highlighting the person's strengths, and one concise sentence highlighting their weaknesses. Be specific and only output two sentences — no bullet points, no extra commentary.

Skill Scores:
{returnStudentSkill}
"""
        feedback_response = self.askGpt(feedback_prompt)

        # Return
        return [returnStudentSkill, feedback_response]
if __name__ == "__main__":
    processor = ResumeProcessor()
    result = processor.processResume("testResume.json")

    print("Skill Summary:")
    print(result[0])  # StudentSkill object
    print("\nFeedback:")
    print(result[1])  # Feedback from OpenAI