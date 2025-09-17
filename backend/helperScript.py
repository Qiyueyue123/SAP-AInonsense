import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv


#This is a helper script to load specific entries to database, add a dictionary and use the db to update
Unemployed = {
  "jobName": "Unemployed",
  "futureJobs": [],
  "jobScore": {
    "Automation/Scripting": 0,
    "Client Management": 0,
    "Code Optimization": 0,
    "Communication": 0,
    "Data Analysis": 0,
    "Database Management": 0,
    "Presentation Skills": 0,
    "Problem Solving": 0,
    "Team Leadership": 0,
    "UI/UX Design": 0
  }
}

#silly config nonsense
load_dotenv()

key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

db = firestore.client()

uploadToDb = db.collection("jobs").document(Unemployed["jobName"])
uploadToDb = db.collection("jobs").document(Unemployed["jobName"]).set(Unemployed)