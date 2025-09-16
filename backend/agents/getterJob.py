import os
from dotenv import load_dotenv


def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterJob(db,uid):
    job = get_user_data(db,uid)["job"]
    return job


def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"


if __name__ == "__main__":
    main()