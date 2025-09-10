## I am going to be implementing my grouping code here
import numpy as np
import random
import string
import copy
from typing import List, Dict, Any

# Constants
NUM_USERS = 20
NUM_PROJECTS = 3
NUM_STATS = 10
MAX_INDIVIDUALS_PER_PROJECT = 5
SKILL_NAMES = [
    "Code Optimization", "Database Management", "Data Analysis", "UI/UX Design",
    "Automation/Scripting", "Communication", "Problem Solving", "Client Management",
    "Team Leadership", "Presentation Skills"
]
JOBS = ["Developer", "Designer", "Analyst", "Engineer", "Manager"]

# Generate a random name
def random_name():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Generate random user pool
def generate_users(num_users: int) -> List[Dict[str, Any]]:
    users = []
    for _ in range(num_users):
        user = {
            "userName": random_name(),
            "assignedProject": None,
            "job": random.choice(JOBS),
            "skills": {skill: random.randint(1, 5) for skill in SKILL_NAMES}
        }
        users.append(user)
    return users

# Generate projects
def generate_projects(num_projects: int, max_individuals: int) -> List[Dict[str, Any]]:
    projects = []
    for i in range(num_projects):
        project = {
            "projectId": f"project_{i+1}",
            "maxIndividuals": max_individuals,
            "assignedEmployees": [],
            "score": 0.0
        }
        projects.append(project)
    return projects

# Normalize vector
def normalize(vec):
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm

# Get user skill vector
def get_skill_vector(user):
    return np.array([user["skills"][skill] for skill in SKILL_NAMES])

# Calculate project vector fit score (normalized projection)
def calculate_project_score(project):
    if not project["assignedEmployees"]:
        return 0.0
    combined_vector = sum([get_skill_vector(emp) for emp in project["assignedEmployees"]])
    proj_vec = normalize(combined_vector)
    total_score = sum(np.dot(normalize(get_skill_vector(emp)), proj_vec) for emp in project["assignedEmployees"])
    avg_score = total_score / len(project["assignedEmployees"])
    return min(avg_score, 1.0)

# Assign initial users randomly to projects
def initial_assignment(users, projects):
    user_pool = users[:]
    random.shuffle(user_pool)
    for project in projects:
        while len(project["assignedEmployees"]) < project["maxIndividuals"] and user_pool:
            user = user_pool.pop()
            project["assignedEmployees"].append(user)
            user["assignedProject"] = project["projectId"]
        project["score"] = calculate_project_score(project)

# Hill climbing: swap 1 user between two projects to improve total score
def hill_climb_optimization(users, projects, generations=1000):
    best_projects = copy.deepcopy(projects)
    best_score = sum(proj["score"] for proj in best_projects)

    for _ in range(generations):
        proj1, proj2 = random.sample(best_projects, 2)
        if not proj1["assignedEmployees"] or not proj2["assignedEmployees"]:
            continue

        emp1 = random.choice(proj1["assignedEmployees"])
        emp2 = random.choice(proj2["assignedEmployees"])

        idx1 = proj1["assignedEmployees"].index(emp1)
        idx2 = proj2["assignedEmployees"].index(emp2)

        proj1["assignedEmployees"][idx1] = emp2
        proj2["assignedEmployees"][idx2] = emp1

        new_score1 = calculate_project_score(proj1)
        new_score2 = calculate_project_score(proj2)

        new_total_score = sum(
            proj["score"] if proj not in [proj1, proj2] else s
            for proj, s in zip(best_projects, [new_score1, new_score2])
        )

        if new_total_score > best_score:
            proj1["score"] = new_score1
            proj2["score"] = new_score2
            emp1["assignedProject"], emp2["assignedProject"] = proj2["projectId"], proj1["projectId"]
            best_score = new_total_score
        else:
            proj1["assignedEmployees"][idx1] = emp1
            proj2["assignedEmployees"][idx2] = emp2

    return best_projects

# --- Run the full pipeline ---
users = generate_users(NUM_USERS)
projects = generate_projects(NUM_PROJECTS, MAX_INDIVIDUALS_PER_PROJECT)
initial_assignment(users, projects)
optimized_projects = hill_climb_optimization(users, projects, generations=500)

# --- Final Output ---
print("Optimized Project Assignments:\n")
for project in optimized_projects:
    print(f"Project ID: {project['projectId']}")
    print(f"  Score: {project['score']:.3f}")
    print("  Assigned Employees:")
    for user in project["assignedEmployees"]:
        print(f"    - {user['userName']} ({user['job']}) -> {user['assignedProject']}")
    print()

for user in users:
    print("Employee ID : "+user["userName"]+"")
    print(user["skills"])
    print(user["assignedProject"])
    print()