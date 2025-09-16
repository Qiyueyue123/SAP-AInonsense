import os
from dotenv import load_dotenv


def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterCourseScore(uid):
    courseScore = get_user_data(uid)["courseScore"]
    return courseScore

def setterCourseScore(db,uid, modifierVector):
    courseScore = getterCourseScore(uid)

    for key, mod_value in modifierVector.items():
        current_value = courseScore.get(key, 0)
        new_value = current_value + mod_value
        # Clamp between 0 and 20
        courseScore[key] = max(0, min(20, new_value))

    db.collection('users').document(uid).update({"courseScore": courseScore})
    return courseScore

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"
    


if __name__ == "__main__":
    main()