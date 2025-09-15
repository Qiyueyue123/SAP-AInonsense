import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agents.pdf_to_image import pdf_page_to_base64
from agents.process_resume import process_resume
from testScoring import ResumeProcessor
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
            return jsonify({"error": "Missing required fields: email or uid or job or targetJob"}), 400
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


@app.route("/upload-resume", methods = ["POST"])
@verify_firebase_token
def upload_resume():
    uid = request.form.get("uid")
    folderPath = 'temp'
    print("UID RECEIVED: " + uid)

    # Create the folder if it doesn't exist
    os.makedirs(folderPath, exist_ok=True)
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['resume']  # Access the uploaded file by name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    base64_image = pdf_page_to_base64(file)
    resume_json = process_resume(base64_image)
    doc_ref = db.collection("users").document(uid)

    unique_id = str(uuid.uuid4())
    filename = f"resume_{unique_id}.json"
    filepath = os.path.join(folderPath, filename)
    with open(filepath, "w") as file:
        json.dump(resume_json,file)
    print(type(filepath))

    json_filepath_for_db = resumeProcessor.restructureJson(filepath)
    with open(json_filepath_for_db, "r") as file:
        json_data = json.load(file)
        doc_ref.set({"resume": json_data}) 

    returnResults = resumeProcessor.processResume(filepath)
    
    print(returnResults)
    returnResultsJSON = {
        "skillScore" : returnResults[0],
        "feedback" : returnResults[1]
    }
    return returnResultsJSON, 200


if __name__ == '__main__':
    app.run(debug=True)