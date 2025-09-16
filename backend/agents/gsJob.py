import os
from dotenv import load_dotenv
from .updateCareerPath import updateCareer


def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterJob(db,uid):
    job = get_user_data(db,uid)["job"]
    return job

def setterJob(db, uid, newJob):
    
    db.collection('users').document(uid).update({"job": newJob})
    CP = updateCareer(db, uid)
    return CP

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"


if __name__ == "__main__":
    main()