import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume

#silly config nonsense
load_dotenv()

key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

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
@app.route("/upload-resume", methods = ["POST"])
@verify_firebase_token
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['resume']  # Access the uploaded file by name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    base64_image = pdf_page_to_base64(file)
    resume_json = process_resume(base64_image)
    print(resume_json)
    return jsonify(resume_json), 200


if __name__ == '__main__':
    app.run(debug=True)