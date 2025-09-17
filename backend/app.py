import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.career_coach import get_chatbot_response, retrieve_relevant_memory, retrieve_short_term_memory
from testScoring import ResumeProcessor
from agents.validCareerChecker import matchJob
from agents.careerPathConstructor import careerPathConstructor
import uuid
import json
from agents.gsTargetScore import assignTargetScore, setterTargetScore
from agents.course import search_courses
from agents.mentor import search_mentors
from agents.edit_resume import edit_resume


# would need to import a function to calculate the targetJobSkillScore based on target job

skillScore = {
  'Client Management':      0.000,
  'UI/UX Design':           0.000,
  'Communication':          0.000,
  'Data Analysis':          0.000,
  'Code Optimization':      0.000,
  'Team Leadership':        0.000,
  'Presentation Skills':    0.000,
  'Database Management':    0.000,
  'Automation/Scripting':   0.000,
  'Problem Solving':        0.000
}

dummyTargetScore = {
  'Client Management':      9.2,
  'UI/UX Design':           5.1,
  'Communication':         15.7,   
  'Data Analysis':         10.8,
  'Code Optimization':     16.3,  
  'Team Leadership':       14.5,
  'Presentation Skills':    7.6,
  'Database Management':   11.9,
  'Automation/Scripting':  12.6,
  'Problem Solving':       17.4    
}
dummyCareerPath = [
    "Software Developer",
    "Senior Software Engineer",
    "Tech Lead",
]

resumeProcessor = ResumeProcessor()
#silly config nonsense
load_dotenv()

key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

db = firestore.client()

app = Flask(__name__)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
print("CORS frontend origin:", frontend_origin)

CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})


@app.after_request
def after_request(response):
    """
    This function runs after each request is processed.
    It adds CORS headers to the response.
    """
    # Adding necessary CORS headers
    response.headers["Access-Control-Allow-Origin"] = os.getenv("FRONTEND_ORIGIN", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"  # Allow methods
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # Allow headers
    # Return the modified response
    return response

#for protecting routes (just put the @verify_firebase_token wrapper for the paths we want to protect)
def verify_firebase_token(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        id_token = auth_header.split(" ", 1)[1]
        try:
            decoded = fb_auth.verify_id_token(id_token)
            request.user = decoded   # uid, email, claims
        except Exception:
            return jsonify({"error": "Invalid/expired token"}), 401
        return f(*args, **kwargs)
    return wrapper


#ROUTES

@app.route("/create-account", methods=["POST"])
def create_account():
    try:
        data = request.get_json()
        print(data)
        email = data.get("email")
        uid = data.get("uid")
        job = data.get("job")
        targetJob = data.get("targetJob")
        # You would run the imported function to calculate score for target job here. Then the mentorScore and courseScore should be the same value.
        if not(email and uid and job and targetJob):
            return jsonify({"error": "Missing required fields: email or uid or job or target job"}), 400
        if matchJob(db,job) == "" or matchJob(db,targetJob) == "":
            return jsonify({"error": "Invalid job or target job. Pick a valid job and target job"}), 400
        else:
            job = matchJob(db,job)
            targetJob = matchJob(db,targetJob)
        users_ref = db.collection("users").document(uid)
        # This will create a new document with the given UID, or update it if it exists

        #would also need to call an imported function to calculate the career path accordingly
        valueToReturn = db.collection('jobs').document(targetJob).get().to_dict().get('jobScore')
        db.collection('users').document(uid).set({"targetScore": valueToReturn}, merge=True)
        currentCareerPath = careerPathConstructor(db, job, targetJob)
        print(currentCareerPath)
        users_ref.set({ "uid": uid,
                        "email": email,
                        "job" : job,
                        "targetJob" : targetJob,
                        "skillScore": skillScore,
                        "mentorScore": valueToReturn,
                        "courseScore": valueToReturn,
                        "careerPath" : currentCareerPath,
                        "courses" : [],
                        "mentors" : [],
                        "resume"  : {}
                          })
        
        
        return jsonify({"message": "Account created successfully", "email": email, "uid": uid}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/upload-resume", methods=["POST"])
@verify_firebase_token
def upload_resume():
    """
    Upload a resume PDF (multipart/form-data, field name 'resume').
    Uses the Firebase token's UID; does not trust a form 'uid'.
    Writes only the 'resume' field (merge) without overwriting other user fields.
    """
    try:
        # ------------------------------------------------------------------------------
        # CHANGED: get uid from verified Firebase token (set in decorator)
        # ------------------------------------------------------------------------------
        uid = getattr(request, "user", {}).get("uid")
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401
        requestResult = request
       

        folderPath = "temp"
        os.makedirs(folderPath, exist_ok=True)
        
        file = requestResult.files["resume"]
        if not file or file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # PDF -> base64 image(s) -> structured resume JSON
        base64_image = pdf_page_to_base64(file)
        resume_json = process_resume(base64_image)

        # Parse to your schema
        json_results = resumeProcessor.parseResponseData(resume_json)
        print("\n[upload-resume] parsed resume results:")
        print(json_results, type(json_results))

        # Optional: persist raw resume JSON to disk
        unique_id = str(uuid.uuid4())
        filename = f"resume_{unique_id}.json"
        filepath = os.path.join(folderPath, filename)
        with open(filepath, "w") as f:
            json.dump(resume_json, f)

        doc_ref = db.collection("users").document(uid)
        json_filepath_for_db = resumeProcessor.restructureJson(filepath)
        with open(json_filepath_for_db, "r") as file:
            json_data = json.load(file)
            doc_ref.update({"resume": json_data}) 

        # Run scoring pipeline
        result_tuple = resumeProcessor.processResume(filepath)
        if not result_tuple:
            result_tuple [skill_score,""]
        # assuming processResume returns (skill_score, feedback)
        skill_score, feedback = result_tuple
        search_courses(uid, db)
        search_mentors(uid, db)
        print("GOOD BYE", skill_score)
        doc_ref.update({"skillScore": skill_score}) 
        print('HELLO')
        return jsonify({"skillScore":skillScore,"feedback":feedback}),200

    except Exception as e:
        # In production, log stacktrace with logging library
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500
    
@app.route("/resume-editor", methods=["GET"])
@verify_firebase_token
def get_resume():
    uid = request.args.get("uid")
    user_ref = db.collection("users").document(uid)
    doc = user_ref.get()
    if doc.exists:
        resume = doc.to_dict().get("resume")
        return jsonify(resume), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/resume-editor/paraphrase", methods=["POST"])
@verify_firebase_token
def paraphrase_section():
    try:
        uid = getattr(request, "user", {}).get("uid")
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401

        data = request.get_json()
        header = data.get("header")
        content = data.get("content")
        text_to_rephrase = data.get("text_to_rephrase")

        if not header or not content or not text_to_rephrase:
            return jsonify({"error": "Missing required fields"}), 400

        # Log input for debugging (optional)
        print(f"Paraphrasing section '{header}' for user {uid}")
        print(f"Original text to rephrase: {text_to_rephrase}")

        paraphrased_text = edit_resume(header, content, mode=1, text_rephrase=text_to_rephrase)

        # Log paraphrased output (optional)
        print(f"Paraphrased text: {paraphrased_text}")

        return jsonify({"paraphrased_text": paraphrased_text}), 200

    except Exception as e:
        print(f"Paraphrase error: {e}", flush=True)
        return jsonify({"error": f"Failed paraphrase: {str(e)}"}), 500
    

@app.route("/resume-editor/update", methods=["POST"])
@verify_firebase_token
def update_resume():
    try:
        uid = getattr(request, "user", {}).get("uid")
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401

        data = request.get_json()
        updated_resume = data.get("resume")
        if updated_resume is None:
            return jsonify({"error": "No resume data provided"}), 400

        user_ref = db.collection("users").document(uid)
        user_ref.set({"resume": updated_resume}, merge=True)

        return jsonify({"message": "Resume updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update resume: {str(e)}"}), 500
    


# ---- Chat: history ----
@app.route("/api/chat/history", methods=["GET"])
@verify_firebase_token
def get_chat_history():
    """
    Returns the last N messages (user + assistant) for the authenticated user.
    """
    try:
        uid = request.user["uid"]
        history = retrieve_short_term_memory(uid, db)  # from agents.career_coach
        return jsonify({"chatHistory": history}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- Chat: send a message ----
@app.route("/api/chat", methods=["POST"])
@verify_firebase_token
def chat():
    """
    Receives a user message, gets an AI reply, and persists BOTH turns to memory.
    """
    try:
        uid = request.user["uid"]
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Call your agent (this will also update short-term/long-term memory)
        ai_response = get_chatbot_response(user_message, uid, db)  # from agents.career_coach
        reply_text = ai_response.get("content") if isinstance(ai_response, dict) else str(ai_response)

        # Optionally return history too (handy for debugging)
        # history = retrieve_short_term_memory(uid, db)
        # return jsonify({"reply": reply_text, "history": history}), 200
        #         
        doc_ref = db.collection("users").document(uid)
        user_doc = doc_ref.get()
        user_data = user_doc.to_dict()
        courses = user_data.get("sortedCourses")
        mentors = user_data.get("sortedMentors")
        stats = user_data.get("skillScore") 
        career_path = user_data.get("careerPath")

        return jsonify({"reply": reply_text, 
                        "skillScore": stats,
                        "careerPath": career_path,
                        "courses": courses,
                        "mentors": mentors}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/career-path", methods=["GET"])
@verify_firebase_token
def get_career_path():
    
    try:

        # Get the UID from the verified Firebase token
        uid = getattr(request, "user", {}).get("uid")
        
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401
        
        doc_ref = db.collection("users").document(uid)
        user_doc = doc_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User profile not found"}), 404
        
        user_data = user_doc.to_dict()
        careerPath = user_data.get("careerPath")
        
        return jsonify({"careerPath":careerPath})
    
    except Exception as e:
        print(f"[ERROR /stats]: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@app.route("/career-path", methods=["POST"])
@verify_firebase_token
def post_career_path():
    try:
        # Get the UID from the verified Firebase token
        uid = getattr(request, "user", {}).get("uid")
        
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401
        
        doc_ref = db.collection("users").document(uid)
        user_doc = doc_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User profile not found"}), 404
        
        user_data = user_doc.to_dict()
        careerPath = user_data.get("careerPath")
        
        return jsonify({"careerPath":careerPath})
    
    except Exception as e:
        print(f"[ERROR /stats]: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/stats", methods=["GET"])
@verify_firebase_token
def get_stats():
    """
    Fetches the user's stats (skills, career path, and recommendations)
    for the main dashboard.
    """
    try:
        # Get the UID from the verified Firebase token
        uid = getattr(request, "user", {}).get("uid")
        if not uid:
            return jsonify({"error": "Unauthenticated"}), 401

        # Fetch the user's document from Firestore
        doc_ref = db.collection("users").document(uid)
        user_doc = doc_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User profile not found"}), 404
        
        user_data = user_doc.to_dict()

        courses = user_data.get("sortedCourses")
        mentors = user_data.get("sortedMentors")
        stats = user_data.get("skillScore") 
        career_path = user_data.get("careerPath")
        
        return jsonify({
            "skillScore": stats,
            "careerPath": career_path,
            "courses": courses,
            "mentors": mentors
        }), 200


    except Exception as e:
        print(f"[ERROR /stats]: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)