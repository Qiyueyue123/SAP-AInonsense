import sys
import os
import json

# --- START: AGGRESSIVE FIX FOR 'frontend' NAME COLLISION ---
# This logic ensures that installed packages in your venv are found before local folders,
# resolving the 'fitz' library's conflict with your 'frontend' directory.
try:
    python_executable = sys.executable
    site_packages = os.path.join(
        os.path.dirname(python_executable),
        'lib',
        f'python{sys.version_info.major}.{sys.version_info.minor}',
        'site-packages'
    )
    if os.path.isdir(site_packages) and site_packages not in sys.path:
        sys.path.insert(0, site_packages)
        print(f"✅ Injected site-packages path to resolve imports: {site_packages}")
except Exception as e:
    print(f"⚠️ Could not modify sys.path for venv: {e}")
# --- END: FIX ---

import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from agents.scoring_agent import score_resume_from_json
from agents.career_coach import get_chatbot_response

load_dotenv()

# --- Initialization ---
try:
    # Ensure this variable name matches your .env file EXACTLY
    key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
    if not key_path:
        raise ValueError("FIREBASE_GOOGLE_CREDENTIALS environment variable not set or found in .env file.")
    
    cred = credentials.Certificate(key_path)
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    firebase_admin.initialize_app(cred, {"projectId": project_id})
    db = firestore.client()
    print("✅ Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Firebase Admin SDK: {e}")
    db = None
    # Exit if Firebase fails to initialize, as the app is unusable.
    sys.exit(1)

app = Flask(__name__)

# --- CORS and Authentication ---
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN")}})

def verify_firebase_token(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token must be a Bearer token"}), 401
        id_token = auth_header.split(" ", 1)[1]
        try:
            decoded = fb_auth.verify_id_token(id_token)
            request.user = decoded
        except Exception as e:
            print(f"Token verification failed: {e}")
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)
    return wrapper

# --- API Routes ---
@app.route("/api/upload-resume", methods=["POST"])
@verify_firebase_token
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        resume_json_str = process_resume(pdf_page_to_base64(file))
        resume_json = json.loads(resume_json_str)

        skill_scores, qualitative_feedback = score_resume_from_json(resume_json)

        user_id = request.user['uid']
        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'resumeAnalysis': resume_json,
            'skillScores': skill_scores,
            'qualitativeFeedback': qualitative_feedback,
            'targetVector': {}
        }, merge=True)
        
        return jsonify({
            "message": "Resume processed and scored successfully!",
            "scores": skill_scores,
            "feedback": qualitative_feedback
        }), 200
    except Exception as e:
        print(f"Error in upload_resume: {e}")
        return jsonify({"error": "Failed to process resume."}), 500

@app.route("/api/chat", methods=["POST"])
@verify_firebase_token
def chat():
    user_id = request.user['uid']
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        user_profile = user_doc.to_dict() if user_doc.exists else {}

        ai_response, updated_profile = get_chatbot_response(user_message, chat_history, user_profile)
        
        if updated_profile:
            user_ref.set(updated_profile, merge=True)

        return jsonify(ai_response), 200
    except Exception as e:
        print(f"Error in chat route: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

