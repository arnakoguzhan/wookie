import json

def isDesign(taskType):
    return taskType == "Design Task"

def isBug(taskType):
    return taskType == "Product Bug"

def isAutomation(taskKey):
    return taskKey.startswith("SEL-")

def isTaskDone(status):
    return status in ["DONE", "Awaiting Release", "Released on Prod", "Pending For Release", "Ready For Release", "Rejected"]

def isTaskReleased(status):
    return status in ["DONE", "Released on Prod", "Ready For Release"]

def getAllTasks(contents):
    return contents['completedIssues'] + contents['issuesNotCompletedInCurrentSprint'] + contents['puntedIssues'] + contents['issuesCompletedInAnotherSprint']

def calculateIndividualMetrics(allTasks, emergedTasksList):
    individualCommittedEffort = {}
    individualDoneEffort = {}
    individualUnDoneEffort = {}
    individualCommittedTaskCount = {}
    individualDoneTaskCount = {}
    individualUndoneTaskCount = {}

    for task in allTasks:
        assigneeName = task['assigneeName']
        taskKey = task['key']
        try:
            taskEffort = task['currentEstimateStatistic']['statFieldValue']['value']
        except:
            taskEffort = 0
        isDone = isTaskDone(task['statusName'])

        if assigneeName not in individualCommittedEffort:
            individualCommittedEffort[assigneeName] = 0
            individualDoneEffort[assigneeName] = 0
            individualUnDoneEffort[assigneeName] = 0
            individualCommittedTaskCount[assigneeName] = 0
            individualDoneTaskCount[assigneeName] = 0
            individualUndoneTaskCount[assigneeName] = 0

        if taskKey not in emergedTasksList:
            individualCommittedEffort[assigneeName] += taskEffort
            individualCommittedTaskCount[assigneeName] += 1
        
        if isDone:
            individualDoneEffort[assigneeName] += taskEffort
            individualDoneTaskCount[assigneeName] += 1
        else:
            individualUnDoneEffort[assigneeName] += taskEffort
            individualUndoneTaskCount[assigneeName] += 1

    return [
        individualCommittedEffort,
        individualDoneEffort,
        individualUnDoneEffort,
        individualCommittedTaskCount,
        individualDoneTaskCount,
        individualUndoneTaskCount
    ]

def calculateTotalMetrics(allTasks, emergedTasksList):
    # General Metrics
    totalEffort = 0
    commitedEffort = 0
    emergedEffort = 0
    doneEffort = 0
    undoneEffort = 0

    # Bug Metrics
    bugTotal = 0
    bugCommited = 0
    bugEmerged = 0
    bugDone = 0
    bugUndone = 0

    # Design Metrics
    designTotal = 0
    designCommited = 0
    designEmerged = 0
    designDone = 0
    designUndone = 0

    # Dev Metrics
    devTotal = 0
    devCommited = 0
    devEmerged = 0
    devDone = 0
    devUndone = 0
    devReleased = 0

    # Pool Metrics
    poolDone = 0
    poolBugDone = 0

    for task in allTasks:
        taskKey = task['key']
        taskType = task['typeName']
        try:
            taskEffort = task['currentEstimateStatistic']['statFieldValue']['value']
        except:
            taskEffort = 0
        isDone = isTaskDone(task['statusName'])
        isReleased = isTaskReleased(task['statusName'])

        totalEffort += taskEffort

        # Emerged Tasks
        if taskKey in emergedTasksList:
            emergedEffort += taskEffort

            if isBug(taskType):
                bugEmerged += taskEffort
            elif isDesign(taskType):
                designEmerged += taskEffort
            else:
                devEmerged += taskEffort

        # Commited Tasks
        else:
            commitedEffort += taskEffort

            if isBug(taskType):
                bugCommited += taskEffort
            elif isDesign(taskType):
                designCommited += taskEffort
            else:
                devCommited += taskEffort

        # Done Tasks
        if isDone:
            doneEffort += taskEffort

            if isBug(taskType):
                bugDone += taskEffort
            elif isDesign(taskType):
                designDone += taskEffort
            else:
                devDone += taskEffort                    

        # Undone Tasks
        else:
            undoneEffort += taskEffort

            if isBug(taskType):
                bugUndone += taskEffort
            elif isDesign(taskType):
                designUndone += taskEffort
            else:
                devUndone += taskEffort

        # Released Tasks
        if isReleased and not (isDesign(taskType) or isAutomation(taskKey)):
            devReleased += taskEffort

    return [
        totalEffort,
        commitedEffort,
        emergedEffort,
        doneEffort,
        undoneEffort,
        bugTotal,
        bugCommited,
        bugEmerged,
        bugDone,
        bugUndone,
        designTotal,
        designCommited,
        designEmerged,
        designDone,
        designUndone,
        devTotal,
        devCommited,
        devEmerged,
        devDone,
        devUndone,
        devReleased,
        poolDone,
        poolBugDone
    ]

def printReport(file):
    sprintReportRaw = json.load(file)

    # Data
    sprintInformation = sprintReportRaw['sprint']
    allTasks = getAllTasks(sprintReportRaw['contents'])
    emergedTasksList = sprintReportRaw['contents']['issueKeysAddedDuringSprint']

    # Total Metrics
    [
        totalEffort,
        commitedEffort,
        emergedEffort,
        doneEffort,
        undoneEffort,
        bugTotal,
        bugCommited,
        bugEmerged,
        bugDone,
        bugUndone,
        designTotal,
        designCommited,
        designEmerged,
        designDone,
        designUndone,
        devTotal,
        devCommited,
        devEmerged,
        devDone,
        devUndone,
        devReleased,
        poolDone,
        poolBugDone
    ] = calculateTotalMetrics(allTasks, emergedTasksList)

    # Individual Metrics
    [
        individualCommittedEffort,
        individualDoneEffort,
        individualUnDoneEffort,
        individualCommittedTaskCount,
        individualDoneTaskCount,
        individualUndoneTaskCount
    ] = calculateIndividualMetrics(allTasks, emergedTasksList)

    return {
        "Sprint Name": sprintInformation['name'],
        "Sprint Goal": sprintInformation['goal'],

        "Total Effort In the Sprint": totalEffort,
        "Commited": commitedEffort,
        "Emerged": emergedEffort,
        "Done": doneEffort,
        "Undone": undoneEffort,

        "Total Bug Effort": bugTotal,
        "Committed Bug Effort": bugCommited,
        "Emerged Bug Effort": bugEmerged,
        "Done Bug Effort": bugDone,
        "Undone Bug Effort": bugUndone,

        "Total Design Effort": designTotal,
        "Commited Design Effort": designCommited,
        "Emerged Design Effort": designEmerged,
        "Done Design Effort": designDone,
        "Undone Design Effort": designUndone,

        "Done Pool Effort": poolDone,
        "Done Pool Bug Effort": poolBugDone,

        "Dev Total": devTotal,
        "Dev Committed": devCommited,
        "Dev Emerged": devEmerged,
        "Dev Done": devDone,
        "Dev Undone": devUndone,
        "Dev Released": devReleased,
        "Shipping Efficiency (%)": devReleased / devCommited * 100 if devCommited > 0 else 0,

        "Sprint Goal Effort (%)": 0,
        "Number of Team Member Participation": 0,

        "Individual Committed Effort": individualCommittedEffort,
        "Individual Committed Task Count": individualCommittedTaskCount,
        "Individual Done Effort": individualDoneEffort,
        "Individual Done Task Count": individualDoneTaskCount,
        "Individual Undone Effort": individualUnDoneEffort,
        "Individual Undone Task Count": individualUndoneTaskCount,
    }