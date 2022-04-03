import csv
import random
from objects import *

##########################################################################
students = [] #array of all the unique student data
    #OBJ-format ==>> id | timestamp | email | fullname | firstname | surname | friends | teachers | lookupName
teachers = [] #array of all the unique teacher data
    #OBJ-format ==>> id | timestamp | email | fullname | firstname | surname | teachers | lookupName
##########################################################################

#will work for any array of objects with 'lookupName's
def findIDbyLookupName(list, request):
    for individual in list:
        if request == individual.lookupName:
            return int(individual.id)

#will work for any array of objects with 'id's
def findPersonByID(list, request):
    for person in list:
        if person.id == request:
            return person

#school email to lookupname
def lookupNameFromEmail(email):
    name = email.split("@")  #cut off email domain
    name = name[0].split(".") #separate names
    return str(name[1]+name[0])

def gradeLevelGraphEdges(G, students, this_grade):
    # print(students[2].__dict__)
    # print(G.__dict__)
    # print(this_grade)
    for student in students:
        # print(student.lookupName," ",student.grade)
        if student.grade == this_grade:
            for peer in student.friends:
                    if peer:
                        peer = findPersonByID(students, peer)
                        if peer and student != peer and peer.grade == this_grade: #no self-reference
                            G.add_edge(student, peer)

#/\/\/\/\/\ foreign keys setup \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
def studentForeignKeys(students):
    #Change Friend/Teacher Request Arrays to foreign keys
    for student in students:
        for request in enumerate(student.friends):
            student.friends[request[0]] = findIDbyLookupName(students, request[1])

def teacherForeignKeys():
    for student in students:
        for request in enumerate(student.teachers):
            student.teachers[request[0]] = findIDbyLookupName(teachers, request[1])

#\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /
# \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#  \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#----------------------------------------------------------------------------------------
# # #test to see how the resolution of the Function impacts things...

def populations(parts_dict):
    pop = []
    for node in parts_dict: pop.append([0,0])
    for node in parts_dict:
        i = parts_dict[node]
        pop[i][0] = i #class number
        pop[i][1] += 1 #class population
    for n in range(1,(pop.count([0,0])+1)): pop.remove([0,0])
    return pop

# # # I know it is a bit messy, be we can refactor later. It is readable-ish.
def graphOptimalLouvianResolutions(G):    
    import community #https://github.com/taynaud/python-louvain
    from tqdm import tqdm
    import matplotlib.pyplot as plt
    import math
    parts_res_pattern=[]

    for i in tqdm(range(1,len(G.nodes)), desc="        Partition Resolution testing"):
        res = i/20
        partitions = community.best_partition(G,resolution=res)
        num_parts = 0
        for node in partitions:
            if partitions[node] > num_parts: num_parts = partitions[node]

        pop = populations(partitions)
        for n in pop: 
            if n[0]>0: parts_res_pattern.append([res,n])
        # sum_pop = 0
        # for n in pop: sum_pop += n
        # avg_pop = math.ceil(sum_pop/len(pop))
        # parts_res_pattern.append([res,avg_pop])
    for i in parts_res_pattern:
        plt.scatter(i[0],i[1][1])
    plt.grid(True)
    plt.ylabel("Average Class Size")
    plt.xlabel("Louvain Partition Resolution Values")
    plt.show()

#dead-ending here: will come back to it...
def isolateLouvianResolutions(G, classSize, minRes, maxRes):    
    import community #https://github.com/taynaud/python-louvain
    import math
    parts_res_pattern=[]
    increment = 10
    spread = math.ceil((maxRes-minRes)*increment)

    for i in range(1,spread):
        res = i/(spread/2)
        partitions = community.best_partition(G,resolution=res)
        num_parts = 0
        for node in partitions:
            if partitions[node] > num_parts: num_parts = partitions[node]

        pop = populations(partitions)
        sum_pop = 0
        for n in pop: sum_pop += n
        avg_pop = math.ceil(sum_pop/len(pop))
        parts_res_pattern.append({
            "resolution":res,
            "avg_pop":avg_pop,
            "pop_dif":math.abs(classSize-avg_pop)
            })
    
    newMinRes = 0
    newMaxRes = 0
    
    sorted(parts_res_pattern,key=lambda x: x[1])
    for i in parts_res_pattern:
        if newMinRes == 0 and i.avg_pop==classSize: newMinRes = i.resolution
        if newMaxRes < i.resolution and i.avg_pop==classSize: newMinRes = i.resolution

    sorted(parts_res_pattern,key=lambda x: x[2])
    if newMinRes == 0: newMinRes=1
    if newMaxRes == 0: newMaxRes=4

    return {
        "maxRes":newMaxRes,
        "minRes":newMinRes
        }

def numberOfPartitions(parts): #a dict of all individuals
    #keys are individuals, values are the part assignment
    num_partitions = 0
    for indv in parts:
        if parts[indv] > num_partitions:
            num_partitions = parts[indv]
    return num_partitions

def makeIntoSections(partitions):
    sections = []
    for part in range(0,numberOfPartitions(partitions)+1):
        new = Section(part)
        sections.append(new)
        for indv in partitions:
            if partitions[indv] == part: sections[part].students.append(indv)
    return sections