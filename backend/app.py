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
from validCareerChecker import matchJob
import uuid
import json
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
        users_ref = db.collection("users").document(uid)
        # This will create a new document with the given UID, or update it if it exists

        #would also need to call an imported function to calculate the career path accordingly
        currentCareerPath = [job] + dummyCareerPath.copy() + [targetJob]
        users_ref.set({ "uid": uid,
                        "email": email,
                        "job" : job,
                        "targetJob" : targetJob,
                        "skillScore": skillScore,
                        "targetScore": dummyTargetScore,
                        "mentorScore": dummyTargetScore,
                        "courseScore": dummyTargetScore,
                        "careerPath" : currentCareerPath
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

        folderPath = "temp"
        os.makedirs(folderPath, exist_ok=True)

        # Validate multipart form + file
        if "resume" not in request.files:
            return jsonify({"error": "No file part 'resume'"}), 400

        file = request.files["resume"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # PDF -> base64 image(s) -> structured resume JSON
        base64_image = pdf_page_to_base64(file)
        resume_json = process_resume(base64_image)

        # Parse to your schema
        json_results = resumeProcessor.parseResponseData(resume_json)
        print("\n[upload-resume] parsed resume results:")
        print(json_results, type(json_results))

        # ------------------------------------------------------------------------------
        # CHANGED: upsert ONLY the "resume" field (no overwrite of other fields)
        # ------------------------------------------------------------------------------
        doc_ref = db.collection("users").document(uid)
        doc_ref.set({"resume": json_results}, merge=True)

        # Optional: persist raw resume JSON to disk
        unique_id = str(uuid.uuid4())
        filename = f"resume_{unique_id}.json"
        filepath = os.path.join(folderPath, filename)
        with open(filepath, "w") as f:
            json.dump(resume_json, f)

        # Run scoring pipeline
        result_tuple = resumeProcessor.processResume(filepath)
        # assuming processResume returns (skill_score, feedback)
        skill_score, feedback = result_tuple if isinstance(result_tuple, (list, tuple)) else (None, None)

        return jsonify({
            "skillScore": skill_score,
            "feedback": feedback
        }), 200

    except Exception as e:
        # In production, log stacktrace with logging library
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('user_message')
#     user_id = request.json.get('user_id')  # Assume user_id is sent with each request
#     user_profile = db.collection('users').document(user_id).get().to_dict()

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('user_message')
#     user_id = request.json.get('user_id')  # Assume user_id is sent with each request
#     user_profile = db.collection('users').document(user_id).get().to_dict()

@app.route("/api/chat/history", methods=["GET"])
@verify_firebase_token
def get_chat_history():
    """
    Fetches the last 10 messages for the authenticated user.
    This matches the endpoint the frontend is calling.
    """
    try:
        user_id = request.user['uid']
        chat_history = retrieve_short_term_memory(user_id, db)
        return jsonify({"chatHistory": chat_history}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
@verify_firebase_token
def chat():
    """
    Receives a message from the user, gets a response from the AI,
    and updates the chat history.
    """
    try:
        user_id = request.user['uid']
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # The get_chatbot_response function handles retrieving history and context
        ai_response = get_chatbot_response(user_message, user_id, db)
        
        # The frontend expects a 'reply' key in the response
        return jsonify({"reply": ai_response.get('content')}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)