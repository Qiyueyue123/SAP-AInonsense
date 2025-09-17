from .getterJob import getterJob
from .getterTargetJob import getterTargetJob
from .careerPathConstructor import careerPathConstructor


def updateCareer(db,uid):
    
    currentJobName = getterJob(db,uid)
    targetJobName = getterTargetJob(db,uid)
    print(currentJobName)
    print(targetJobName)

    careerPath = careerPathConstructor(db, currentJobName, targetJobName)
    
    db.collection('users').document(uid).update({"careerPath": careerPath})
    
    return careerPath