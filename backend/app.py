import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# --- Import your custom agents and classes ---
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.career_coach import get_chatbot_response
from testScoring import ResumeProcessor # Using the class from your testScoring.py

# --- Initialization ---
load_dotenv()
db = None
try:
    # Initialize your scoring class instance
    resume_processor = ResumeProcessor()
    
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS path not found in .env file.")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "projectId": os.getenv("FIREBASE_PROJECT_ID")
    })
    db = firestore.client()
    print("✅ Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"❌ ERROR: Failed to initialize backend: {e}")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")}})

# --- Authentication Decorator 
def verify_firebase_token(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "): return jsonify({"error": "Missing Bearer token"}), 401
        id_token = auth_header.split(" ", 1)[1]
        try:
            request.user = fb_auth.verify_id_token(id_token)
        except Exception as e:
            return jsonify({"error": f"Invalid or expired token: {e}"}), 401
        return f(*args, **kwargs)
    return wrapper

# --- API Routes ---

@app.route("/create-account", methods=["POST"])
def create_account():
    
    try:
        data = request.get_json()
        email = data.get("email")
        uid = data.get("uid")
        if not email or not uid:
            return jsonify({"error": "Missing required fields: email or uid"}), 400
        users_ref = db.collection("users").document(uid)
        users_ref.set({"uid": uid, "email": email}, merge=True)
        return jsonify({"message": "Account created successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# This route now saves both resume data and scores to Firestore.
@app.route("/api/upload-resume", methods=["POST"])
@verify_firebase_token
def upload_resume():
    if 'resume' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['resume']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    try:
        # Step 1 & 2: Process the PDF into structured JSON
        base64_image = pdf_page_to_base64(file)
        resume_json = process_resume(base64_image)

        # Step 3: Score the resume JSON using your class
        
        skill_summary_obj, feedback_str = resume_processor.processResume(resume_json, from_file=False)
        skill_scores = skill_summary_obj.to_dict()

        # Step 4: Save everything to the database
        user_id = request.user['uid']
        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'resumeJson': resume_json,             # The raw structured resume
            'skillScores': skill_scores,            # The calculated skill vectors
            'qualitativeFeedback': feedback_str,
            'targetVector': {}                      # Initialize empty target vector
        }, merge=True)

        print(f"✅ Successfully processed and saved data for user {user_id}")
        return jsonify({"message": "Resume processed and saved successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

# This is the new endpoint for chatbot.
@app.route("/api/chat", methods=["POST"])
@verify_firebase_token
def chat():
    user_id = request.user['uid']
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])

    if not user_message: return jsonify({"error": "No message provided"}), 400

    try:
        # **READ FROM DATABASE**
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return jsonify({"error": "User profile not found. Please upload a resume first."}), 404
        user_profile = user_doc.to_dict()
        user_profile['uid'] = user_id

        # Pass the user's data and the db client to the chatbot
        ai_response = get_chatbot_response(user_message, chat_history, user_profile, db)
        
        return jsonify(ai_response), 200
        
    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    if db is not None:
        app.run(debug=True, port=5000)
    else:
        print("❌ Could not start Flask server because Firebase initialization failed.")

