import os
from dotenv import load_dotenv




def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterTargetScore(uid):
    targetScore = get_user_data(uid)["targetScore"]
    return targetScore
def assignTargetScore(db, uid, jobName):
    try:
        valueToReturn = db.collection('jobs').document(jobName).get().to_dict().get('jobScore')
        db.collection('users').document(uid).set({"targetScore": valueToReturn}, merge=True)
        return valueToReturn
    except Exception as e:
        print(f"Error assigning target score for job '{jobName}' and user '{uid}': {e}")
    return valueToReturn
def setterTargetScore(db, uid, modifierVector):
    targetScore = getterTargetScore(uid)

    for key, mod_value in modifierVector.items():
        current_value = targetScore.get(key, 0)
        new_value = current_value + mod_value
        # Clamp between 0 and 20
        targetScore[key] = max(0, min(20, new_value))

    db.collection('users').document(uid).update({"TargetScore": targetScore})
    return targetScore


def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"



if __name__ == "__main__":
    main()