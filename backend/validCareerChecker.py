from sentence_transformers import SentenceTransformer, util
import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
import os
import json
from dotenv import load_dotenv

model = SentenceTransformer('all-MiniLM-L6-v2')
def similarityScore(model,text, keyword):
        return util.cos_sim(
            model.encode(text),
            model.encode(keyword)
        )[0][0].item()
def matchJob(db, input_job_title, threshold=0.75):
    listOfPossibleJobs = []
    

    
    jobsRef = db.collection('jobs')
    jobs = jobsRef.stream()
    for job in jobs:
        data = job.to_dict()
        if "jobName" in data:

            currentSimilarityScore = similarityScore(model,input_job_title,data["jobName"])
            if(currentSimilarityScore > threshold):
                 listOfPossibleJobs.append([data["jobName"],currentSimilarityScore])
        
    listOfPossibleJobs.sort(key=lambda x: x[1], reverse=True)
    if len(listOfPossibleJobs) == 0:
         return ""
    
    return listOfPossibleJobs[0][0]
    
