import random
from functions import *

class Section:
    def __init__(self,roster,grade):
        self.roster = roster
        self.teachers = []
        self.grade = grade

    def __hash__(self):      #make sections available as keys
        return hash(self)

    def __eq__(self, other): #make sections available as keys
        return (self.__hash__ == other.__hash__)

    def __ne__(self, other): #make sections available as keys
        return not(self.__hash__ == other.__hash__)
    
    def missingTeachers(self):
        if len(self.teachers)==0:
            return True
        else:
            return False

class Dyad:
    def __init__(self,teacher1,teacher2):
        self.teacher1 = teacher1
        self.teacher2 = teacher2
        self.sectionVotes = [] #[section.id, votes]
        self.totalVotes = 0
        self.unplaced = True
    
    def __hash__(self):      #make dyads available as keys
        return hash((self.id))

    def __eq__(self, other): #make dyads available as keys
        return (self.__hash__) == (other.__hash__)

    def __ne__(self, other): #make dyads available as keys
        return not(self.__hash__ == other.__hash__)

    def votesCount(self, sections):
        for section in sections:
            votes = 0
            for student in section.roster:
                for teacher in student.teachers:
                    if teacher == self.teacher1.lookupName: votes += 1
                    if teacher == self.teacher2.lookupName: votes += 1
            self.sectionVotes.append([section,votes])
        self.sumVotes()
    
    def sumVotes(self):
        for section in self.sectionVotes:
            self.totalVotes += section[1]


# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\   
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \
#    \/    \/    \/    \/    \/    \/    \/    \/    \/  

class Person:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
        self.lookupName = ''
    
    def __hash__(self):      #make people available as keys
        return hash((self.id))

    def __eq__(self, other): #make people available as keys
        return (self.__hash__) == (other.__hash__)

    def __ne__(self, other): #make people available as keys
        return not(self.__hash__ == other.__hash__)

    #go from 'Joe Smith' to 'joesmith'
    def simpleFullName(self, name):
        arr = [x.strip() for x in name.split(' ')]
        sum_name = ''
        for i in arr:
            sum_name += i
        return sum_name.lower()

class Student(Person):
    def makeFriendsRequestArray(self):
        temp_friends = []
        #forced into repetative code by Google Forms...
        if isinstance(self.peer1, str):
            self.peer1 = self.simpleFullName(self.peer1)
            temp_friends.append(self.peer1)
            del self.peer1
        if isinstance(self.peer2, str):
            self.peer2 = self.simpleFullName(self.peer2)
            temp_friends.append(self.peer2)
            del self.peer2
        if isinstance(self.peer3, str):
            self.peer3 = self.simpleFullName(self.peer3)
            temp_friends.append(self.peer3)
            del self.peer3
        if isinstance(self.peer4, str):
            self.peer4 = self.simpleFullName(self.peer4)
            temp_friends.append(self.peer4)
            del self.peer4
        if isinstance(self.peer5, str):
            self.peer5 = self.simpleFullName(self.peer5)
            temp_friends.append(self.peer5)
            del self.peer5
        self.friends = temp_friends

    def makeTeachersRequestArray(self):
        temp = self.teachers.split(",") #split() returns a list
        self.teachers = []
        for i in range(0,int(len(temp)/2)):
            lastname = temp[2*i]
            firstname = temp[2*i+1]
            name = self.simpleFullName(firstname+lastname)
            self.teachers.append(name)

class Teacher(Person):
    def intentionallybBlank():
        return

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\   
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \
#    \/    \/    \/    \/    \/    \/    \/    \/    \/  
class TestResults:
    def __init__(self,res_used,biggest_part,avg_pop,pop_dif,numParts,works):
        self.resolution=res_used
        self.biggest_part=biggest_part
        self.avg_pop=avg_pop
        self.pop_dif=pop_dif
        self.numParts=numParts
        self.works=works

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\   
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \
#    \/    \/    \/    \/    \/    \/    \/    \/    \/  

import networkx as nx
import community #https://github.com/taynaud/python-louvain
import math

class GraphData:
    def __init__(self, students, grade, idealClassSize,**kwargs):
        self.graph = nx.Graph() #nondirectional empty graph
        self.students = students #only pass in students of a certain grade
        self.idealClassSize = idealClassSize
        self.grade = grade  #number for reference
        #-----------------------------------------
        self.parts = []     #partitions to keep
        self.census = []    #partition populations
        self.numParts = 0   #for easy reference
        self.resolution = 1 #default resolution
        #-----------------------------------------
        self.colors = []    #for graphing
        self.labeldict = {} #for graphing
        self.hues=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080']
        self.__dict__.update(kwargs)


    def defineGraphEdges(self):
        for student in self.students:
            for peer in student.friends:
                if peer:
                    peer = findPersonByID(self.students, peer)
                    if peer and student != peer: #no self-reference
                        self.graph.add_edge(student, peer)
        print("\tGrade",self.grade,self.graph) #readable report for making this graph

    def partsCount(self, parts): #a dict of all individuals' partition assignments
        #keys are individuals, values are the part assignment
        num = 0
        for node in parts:
            if parts[node] > num:
                num = parts[node]
        if parts: num+=1 #b/c zero-referenced partitions
        return num #return Zero if no parts

    def sectionCensus(self, parts): #can be for temporary parts as well
        pop = []
        for node in parts: pop.append([0,0]) #make enough empty parts
        for node in parts:
            i = parts[node] #get partition number
            pop[i][0] = i #define/redefine number
            pop[i][1] += 1 #increase part population
        for n in range(1,(pop.count([0,0])+1)): pop.remove([0,0]) #remove empty parts
        return pop #2D array [part#, population]

    def compareToIdeal(self, res_used, parts):
        pop = self.sectionCensus(parts)
        numParts = self.partsCount(parts)
        sum_pop = 0
        biggest_part = 0
        for n in pop: 
            if n[1] > biggest_part: biggest_part = n[1]
            sum_pop += n[1]
        avg_pop = sum_pop/len(pop)
        #----- define actual testing criteria
        remaining = len(self.students)-sum_pop   #remaining students to place
        totalSeats = len(pop)*self.idealClassSize #enough seats to fit all students
        #----- tests ------------------------
        canFitEveryone = False
        noneBiggerThanIdeal = False
        reasonableNumOfSections = False
        if totalSeats-(len(self.parts) + remaining) > 0: canFitEveryone = True
        if biggest_part <= self.idealClassSize: noneBiggerThanIdeal = True
        if totalSeats*1.10 < len(self.students): reasonableNumOfSections = True
        if canFitEveryone and noneBiggerThanIdeal and reasonableNumOfSections:
            works = True #if the conditions are met
        else: works = False #not enough seats in this configuration
        return {"resolution": float(res_used),
                "biggest_part": biggest_part,
                "avg_pop":avg_pop,
                "pop_dif": abs(self.idealClassSize-avg_pop),
                "numParts": numParts,
                "works":works}

    def simplePartitions(self):
        self.parts = community.best_partition(self.graph) #the resolution seems like it can be anywhere from 1.0 to 0.2n

    
    def handleRandomInResolution(self, minRes, maxRes, avg, asymptote, increment):            
        pattern=[]
        resDiff = maxRes-minRes
        spread = math.ceil(resDiff*increment)
        asymptote.append(spread)
        newMinRes = 0.0
        newMaxRes = 0.0
        sumRes = 0
        countWorking = 0

        for i in range(spread):
            res = (i/spread)*resDiff 
            if avg == 1: res += minRes
            else: res += avg-(resDiff/2)
            parts = community.best_partition(self.graph,resolution=res)
            results = self.compareToIdeal(res, parts)
            pattern.append(results)
        
        sorted(pattern,key=lambda x: x["resolution"])
        for j in pattern:
            # print(j)
            if j["works"]:
                sumRes += j["resolution"]
                countWorking += 1
                if newMinRes == 0.0: newMinRes = j["resolution"]
                if newMaxRes <= j["resolution"]: newMaxRes = j["resolution"]
        if countWorking == 0: avg = 1
        else: avg = sumRes/countWorking
        if newMaxRes == 0: newMaxRes=10        
        results = {"minR":newMinRes,"maxR":newMaxRes,"avg":avg,"asymptote":asymptote,"inc":increment}
        return results

    def recursiveAsymptoteToIdealRes(self, t, num):
        for n in range(25):
            # print("\t\t",t)
            if len(t["asymptote"]) >= 3:
                if t["asymptote"][-3] <= (t["asymptote"][-1]*1.25): break
            t = self.handleRandomInResolution(t["minR"],t["maxR"],t["avg"],t["asymptote"],num)
        return t["avg"]

    def calibratedPartitions(self, res):
        parts = community.best_partition(self.graph,resolution=res)
        results = self.compareToIdeal(res, parts)
        if results["works"]:
            self.parts = parts
            self.numParts = self.partsCount(self.parts)
            self.census = self.sectionCensus(self.parts)
        else:
            self.calibratedPartitions(res)

    def expandSectionsToFitStudents(self):
        new_sections = (len(self.students) - (self.numParts*self.idealClassSize))/self.idealClassSize
        for section in range(0,math.ceil(new_sections)):
            if len(self.census)==0:self.census.append([0,0])
            self.census.append([self.census[-1][0]+1,0])
        self.numParts = len(self.census)

    def uplacedStudentsInRandomParts(self, grade_list):
        unplaced = []
        for student in grade_list:
            if student not in self.parts:
                unplaced.append(student)
        random.shuffle(unplaced)
        while unplaced:
            lost_soul = unplaced.pop(-1)
            for part in self.census:
                if part[1] < self.idealClassSize: 
                    opening = part[0]
                    part[1] += 1
                    break
            self.parts[lost_soul] = opening

    def addToMainSections(self, sections):
        this_id = len(sections)
        for section in range(self.numParts):
            grade = self.grade
            roster = []
            for student in self.parts:
                if self.parts[student] == section: 
                    roster.append(student)
            sections.append(Section(roster,grade))
            this_id += 1    #want unique section numbers for export
            sections[-1].id = this_id
        

    def setColorsAndLabels(self):
        for node in self.parts:
            self.colors.append(
                self.hues[self.parts[node] % len(self.hues)])
            self.labeldict[node] = self.parts[node]