import os
from dotenv import load_dotenv
from .updateCareerPath import updateCareer
from .validCareerChecker import matchJob


def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterJob(db,uid):
    job = get_user_data(db,uid)["job"]
    return job

def setterJob(db, uid, newJob):
    if(matchJob(db,newJob) == ""):
        return
    else:
        print('ERROR HERE 20')
        newJob = matchJob(db,newJob)
    print('ERROR HERE 22')
    db.collection('users').document(uid).update({"job": newJob})
    print('ERROR HERE 24')
    CP = updateCareer(db, uid)
    print('ERROR HERE 26')
    return CP

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"


if __name__ == "__main__":
    main()