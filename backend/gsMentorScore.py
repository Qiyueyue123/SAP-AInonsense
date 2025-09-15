import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth as fb_auth, credentials, firestore
#silly config nonsense
load_dotenv()

key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})

db = firestore.client()



def get_user_data(uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterMentorScore(uid):
    mentorScore = get_user_data(uid)["mentorScore"]
    return mentorScore

def setterMentorScore(uid, modifierVector):
    mentorScore = getterMentorScore(uid)

    for key, mod_value in modifierVector.items():
        current_value = mentorScore.get(key, 0)
        new_value = current_value + mod_value
        # Clamp between 0 and 20
        mentorScore[key] = max(0, min(20, new_value))

    db.collection('users').document(uid).update({"mentorScore": mentorScore})
    return mentorScore

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"
    print(getterMentorScore(test_uid))
    print(setterMentorScore(test_uid,{}))


if __name__ == "__main__":
    main()