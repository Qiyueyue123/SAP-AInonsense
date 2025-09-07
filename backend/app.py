import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv


#silly config nonsense
load_dotenv()

key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})


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


if __name__ == '__main__':
    app.run(debug=True)