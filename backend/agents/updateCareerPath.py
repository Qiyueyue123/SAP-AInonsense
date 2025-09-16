from .gsJob import getterJob
from .gsTargetJob import getterTargetJob
from .careerPathConstructor import careerPathConstructor


def updateCareer(db,uid):
    currentJobName = getterJob(db,uid)
    targetJobName = getterTargetJob(db,uid)
    

    careerPath = careerPathConstructor(db, currentJobName, targetJobName)

    db.collection('users').document(uid).update({"careerPath": careerPath})
    return careerPath