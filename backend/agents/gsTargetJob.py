import os
from dotenv import load_dotenv
from .updateCareerPath import updateCareer

def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterTargetJob(db,uid):
    targetJob = get_user_data(db,uid)["targetJob"]
    return targetJob

def setterTargetJob(db, uid, newTargetJob):
    
    db.collection('users').document(uid).update({"targetJob": newTargetJob})
    CP = updateCareer(db, uid)
    return CP

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"


if __name__ == "__main__":
    main()