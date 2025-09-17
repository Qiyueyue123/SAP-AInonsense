import heapq



def calculateCostFromVector(jobA,jobB):
    #A stands for current
    #Used for heuristic calculation + actual calculation if no pointer
    totalCost = 0
   
    for skill in jobA["jobScore"].keys():
        
        totalCost += max(jobA["jobScore"][skill],jobB["jobScore"][skill]) - jobA["jobScore"][skill]
    return totalCost
def predictedCost(currentJob, nextJob, targetJob, pointerToNextJob = True):
    totalCost = 0
    if pointerToNextJob:
        totalCost += calculateCostFromVector(nextJob, targetJob) + 1
    else:
        totalCost += calculateCostFromVector(currentJob, nextJob)
        totalCost += calculateCostFromVector(nextJob, targetJob)
    return totalCost
def updateSeenJobs(seenDict, jobName, path, cost):
    if jobName not in seenDict:
        seenDict[jobName] = (path, cost)
    elif cost < seenDict[jobName][1]:
        seenDict[jobName] = (path, cost)


def careerPathConstructor(db, currentJob, targetJob):
    # currentJob and targetJob should be the jobName or a string
    
    jobsRef = db.collection('jobs')
    jobs = jobsRef.stream()
   
    dictionaryOfJobs = {}
    for job in jobs:
        data = job.to_dict()
        dictionaryOfJobs[data["jobName"]] = data
    
    
    dictionaryOfSeenJobs = {}
   
    currentNode = dictionaryOfJobs[currentJob]
    targetNode = dictionaryOfJobs[targetJob]
    cameFrom = []
    
    currentDistance = 0
    
    dictionaryOfSeenJobs[currentNode["jobName"]] = (cameFrom, currentDistance)
    
    # using a pointer is considered a cost of 1
    priorityQ = []
    # to treat as a heapq, use heapq.heappush(priorityQ, (cost, nextJobName))
   
    for jobName in dictionaryOfJobs.keys():
        if jobName in currentNode["futureJobs"]:
            cost = predictedCost(currentNode, dictionaryOfJobs[jobName], targetNode)
            heapq.heappush(priorityQ, (cost, jobName))
            updateSeenJobs(dictionaryOfSeenJobs, jobName, cameFrom + [currentNode["jobName"]], cost)
        elif jobName != currentNode["jobName"]:
            cost = predictedCost(currentNode, dictionaryOfJobs[jobName], targetNode, False)
            heapq.heappush(priorityQ, (cost, jobName))
            updateSeenJobs(dictionaryOfSeenJobs, jobName, cameFrom + [currentNode["jobName"]], cost)
    i = 100
    
    while (len(priorityQ) > 0 and i > 0):
        i -= 1
        # just in case this garbage doesnt work
        if currentNode["jobName"] == targetNode["jobName"]:
            returnArray = dictionaryOfSeenJobs[currentJobName][0] + [targetNode["jobName"]]
            return returnArray
        currentCost, currentJobName = heapq.heappop(priorityQ)
        currentNode = dictionaryOfJobs[currentJobName]
        for jobName in dictionaryOfJobs.keys():
            if jobName in currentNode["futureJobs"]:
                cost = predictedCost(currentNode, dictionaryOfJobs[jobName], targetNode)
                heapq.heappush(priorityQ, (cost, jobName))
                updateSeenJobs(dictionaryOfSeenJobs, jobName, dictionaryOfSeenJobs[currentNode["jobName"]][0] + [currentNode["jobName"]], cost)
            elif jobName != currentNode["jobName"]:
                cost = predictedCost(currentNode, dictionaryOfJobs[jobName], targetNode, False)
                heapq.heappush(priorityQ, (cost, jobName))
                updateSeenJobs(dictionaryOfSeenJobs, jobName, dictionaryOfSeenJobs[currentNode["jobName"]][0] + [currentNode["jobName"]], cost)
    if i < 0:
        print("BROKEN CAREER PATH CONSTRUCTOR")
    return [currentJob, targetJob]
