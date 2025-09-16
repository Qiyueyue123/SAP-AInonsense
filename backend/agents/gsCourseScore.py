import os
from dotenv import load_dotenv
from .course import search_courses


def get_user_data(db,uid):
    userRef = db.collection('users').document(uid)
    userDoc = userRef.get().to_dict()
    return userDoc

def getterCourseScore(db, uid):
    courseScore = get_user_data(db, uid)["courseScore"]
    return courseScore

def setterCourseScore(db, uid, modifierVector):
    courseScore = getterCourseScore(db, uid)

    for key, mod_value in modifierVector.items():
        current_value = courseScore.get(key, 0)
        new_value = current_value + mod_value
        # Clamp between 0 and 20
        courseScore[key] = max(0, min(20, new_value))

    db.collection('users').document(uid).update({"courseScore": courseScore})
    new_course_list = search_courses(uid, db)
    return new_course_list
    

def main():
    test_uid = "28q1SUuhhCRnfJgd0mdM6NcflLr2"
    


if __name__ == "__main__":
    main()