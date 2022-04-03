import os
import csv
import glob
from objects import *
from functions import *

#\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /
# \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  / 
#  \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/  
#------------- PREAMBLE -------------------------------------------------

idealClassSize = 16 #the number of students we want in a class
partitioning_resolution = 1 #number taken from testing function output
number_of_tests = 100 #self-calibration tests: higher number, longer time
# use 100 while testing
# use 1000 while running the real thing.

students=[]
teachers=[]
sections=[]

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Import & clean STUDENT data from survey/ known roster---------------
# STEP-01: Import student-survey data (as Student objects)
with open('real-data/tester-students.csv') as csvfile:
        studentReader = csv.DictReader(csvfile, delimiter=',')
        #------------- main students objects & array ----------------------
        for row in studentReader:
            students.append(Student(**row))
            new = students[-1] #shorten the reference name
            new.id = 0 #filler id, until STEP 2-B
            new.makeFriendsRequestArray() #formatted as simpleFullName-s
            new.makeTeachersRequestArray()
            new.lookupName = new.simpleFullName(new.full_name)
            new.grade = 0 #filler number-grade, until STEP 2-B

        print("\t", len(students), "\tunique Student-s in 'students' array, from survey")
        # print(students[0].__dict__) #check contents of new Student object

# STEP-02: Use 'known' student roster (sort roster first)
# === 2-A. find student ID numbers, for student objects
with open('real-data/2023studentroster.csv') as csvfile:
        rosterReader = csv.DictReader(csvfile, delimiter=',')
        #------------- Get Student ID numbers -----------------------------
        ref_array = []
        for row in rosterReader:
            ref_array.append(Student(**row))
            new = ref_array[-1] #shorten the reference name
            name = new.firstName + new.lastName
            new.lookupName = new.simpleFullName(name)

        print("\t", len(ref_array), "\tunique Student-s in 'known roster' array")
        # print(ref_array[1].__dict__) #check contents of Roster info

# === 2-B. add in any students who did not complete survey
for stu in ref_array:
    found_them = False
    for n in students:
        if stu.lookupName == n.lookupName:
            found_them = True
            n.id = int(stu.studentNumber)
            n.grade = int(stu.nextGrade)
    if not found_them:
        students.append(stu)
        new = students[-1] #shorten the reference name
        new.id = int(stu.studentNumber)
        new.friends=[]  #no requested peers
        new.teachers=[] #no requested teachers
        new.grade = int(stu.nextGrade)

print("\t", len(students), "\tunique Student-s in 'students' array")
# for n in students: 
#     if n.id==1901696:
#         print(n.__dict__)

# === 2-C. identify all student-survey data that needs 'cleaned'
dataToBeCleaned=[] #this is for all name entry errors in 2-C & 2-D

for i in students:
    for j in ref_array:
        if i.lookupName == j.lookupName:
            i.accountedFor = True
            break
        else:
            i.accountedFor = False
for i in students:
    if i.accountedFor == False:
        dataToBeCleaned.append([i.lookupName])

# print(students[4].__dict__) #early entries come from the survey

# === 2-D. change all peer requests to foreign keys
for student in students:
    friend_error=[]
    for request in enumerate(student.friends):
        if request[1]: #if it is not empty
            friendID = findIDbyLookupName(students, request[1])
            if friendID:
                student.friends[request[0]] = findIDbyLookupName(students, request[1])
            else:
                friend_error.append(request[1])
    if friend_error:
        dataToBeCleaned.append([student.lookupName,friend_error])

# STEP-03: Report all data that needs manually 'cleaned' from name entries in survey
files = glob.glob('data-entry-errors.csv')
for f in files:
    try:
        os.remove(f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))

if dataToBeCleaned: #this is for all name entry errors in 2-C & 2-D
    print("\tFound invalid student name entries. Gerneated 'data-entry-errors.csv' file.")
    print("\t", len(dataToBeCleaned), "\tStudents input invalid names")

    # for n in enumerate(dataToBeCleaned):
    #     print("\t\t"+str(n[1]))

    #make new CSV files
    with open('data-entry-errors.csv', 'w', newline='\n') as csvfile:
        output = csv.writer(csvfile, delimiter=',')
        for i in enumerate(dataToBeCleaned): output.writerow(dataToBeCleaned[i[0]])

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Import & clean TEACHER data from survey/ known roster --------------
# STEP-04. Import teacher-survey data
with open('real-data/tester-teachers.csv') as csvfile:
        teacherReader = csv.DictReader(csvfile, delimiter=',')
        #------------- main teachers objects & array ----------------------
        this_id = 0
        for row in teacherReader:
            this_id +=1
            teachers.append(Teacher(**row))
            new = teachers[-1]
            new.id = this_id
            name = new.email.split("@") #breakupEmail | part 1
            name = name[0].split(".")   #breakupEmail | part 2
            new.lookupName = lookupNameFromEmail(new.email)

        print("\t", len(teachers), "\tunique Teacher-s in 'teachers' array, from survey")
        # print(teachers[1].__dict__) #check contents of Roster info

# STEP-05. Use 'known' teacher roster (sort roster first)
# === 5-A. add in teachers who did not complete survey
# === 5-B. assign unique ID/email/lookup name <-------------- maybe not...

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Repeated steps for all 4 grades ------------------------------------
# STEP-06. Build Graph data from all student requests
import networkx as nx
import matplotlib.pyplot as plt

freshmen=[] 
sophomores=[] 
juniors=[] 
seniors=[]

for student in students:
    if student.grade == 9: freshmen.append(student)
    if student.grade ==10: sophomores.append(student)
    if student.grade ==11: juniors.append(student)
    if student.grade ==12: seniors.append(student)

Freshmen   = GraphData(freshmen,    9, idealClassSize)
Sophomores = GraphData(sophomores, 10, idealClassSize)
Juniors    = GraphData(juniors,    11, idealClassSize)
Seniors    = GraphData(seniors,    12, idealClassSize)

# for n in students:
#     print(n.lookupName," ",n.grade)
Freshmen.defineGraphEdges()
Sophomores.defineGraphEdges()
Juniors.defineGraphEdges()
Seniors.defineGraphEdges()

# STEP-07. Partition students from Graph data ---
# === 7-A. Test to find ideal LouvianResolution
starting_minRes = 0.001
starting_maxRes = 10
starting_avgRes = 1
# number_of_tests = 100 #<-------------- make 1000 for real deal...
if Freshmen.graph:
    print("\t\tFinding ideal resolution for Freshmen.")
    first_test = Freshmen.handleRandomInResolution(starting_minRes,starting_maxRes,starting_avgRes,[],number_of_tests) #shot in the dark
    Freshmen.resolution = Freshmen.recursiveAsymptoteToIdealRes(first_test, number_of_tests)
    print("\t\tFound resolution:",Freshmen.resolution)
if Sophomores.graph:
    print("\t\tFinding ideal resolution for Sophomores.")
    first_test = Sophomores.handleRandomInResolution(starting_minRes,starting_maxRes,starting_avgRes,[],number_of_tests) #shot in the dark
    Sophomores.resolution = Sophomores.recursiveAsymptoteToIdealRes(first_test, number_of_tests)
    print("\t\tFound resolution:",Sophomores.resolution)
if Juniors.graph:
    print("\t\tFinding ideal resolution for Juniors.")
    first_test = Juniors.handleRandomInResolution(starting_minRes,starting_maxRes,starting_avgRes,[],number_of_tests) #shot in the dark
    Juniors.resolution = Juniors.recursiveAsymptoteToIdealRes(first_test, number_of_tests)
    print("\t\tFound resolution:",Juniors.resolution)
if Seniors.graph:
    print("\t\tFinding ideal resolution for Seniors.")
    first_test = Seniors.handleRandomInResolution(starting_minRes,starting_maxRes,starting_avgRes,[],number_of_tests) #shot in the dark
    Seniors.resolution = Seniors.recursiveAsymptoteToIdealRes(first_test, number_of_tests)
    print("\t\tFound resolution:",Seniors.resolution)

# === 7-B. Actually partition students into seperate sections, from tests above
if Freshmen.resolution != 1:
    Freshmen.calibratedPartitions(Freshmen.resolution)
if Sophomores.resolution != 1:
    Sophomores.calibratedPartitions(Sophomores.resolution)
if Juniors.resolution != 1:
    Juniors.calibratedPartitions(Juniors.resolution)
if Seniors.resolution != 1:
    Seniors.calibratedPartitions(Seniors.resolution)

total_parts = Freshmen.numParts + Sophomores.numParts + Juniors.numParts + Seniors.numParts
print("\t",total_parts," automatically generated partitions")

# STEP-08. merge all graph data for an image (just for fun)
Freshmen.setColorsAndLabels()
Sophomores.setColorsAndLabels()
Juniors.setColorsAndLabels()
Seniors.setColorsAndLabels()

if Freshmen.parts:
    nx.draw(Freshmen.graph, node_color=Freshmen.colors, node_size=175, labels=Freshmen.labeldict, with_labels = True)
    plt.savefig("freshmen.png", dpi=200)
    plt.clf() #so the saved and displayed graph doesn't overlap "clear"
if Sophomores.parts:
    nx.draw(Sophomores.graph, node_color=Sophomores.colors, node_size=175, labels=Sophomores.labeldict, with_labels = True)
    plt.savefig("sophomores.png",dpi=200)
    plt.clf() #so the saved and displayed graph doesn't overlap "clear"
if Juniors.parts:
    nx.draw(Juniors.graph, node_color=Juniors.colors, node_size=175, labels=Juniors.labeldict, with_labels = True)
    plt.savefig("juniors.png",   dpi=200)
    plt.clf() #so the saved and displayed graph doesn't overlap "clear"
if Seniors.parts:
    nx.draw(Seniors.graph, node_color=Seniors.colors, node_size=175, labels=Seniors.labeldict, with_labels = True)
    plt.savefig("seniors.png",   dpi=200)
    plt.clf() #so the saved and displayed graph doesn't overlap "clear"


# STEP-09. Add students without Graph requests to the partitions, maintaining max & even class sizes
#only run this if there are any students in the grade from survey
if Freshmen.parts and Freshmen.numParts*idealClassSize < len(Freshmen.students):
    Freshmen.expandSectionsToFitStudents()
    Freshmen.uplacedStudentsInRandomParts(freshmen)

if Sophomores.parts and Sophomores.numParts*idealClassSize < len(Sophomores.students):
    Sophomores.expandSectionsToFitStudents()
    Sophomores.uplacedStudentsInRandomParts(sophomores)

if Juniors.parts and Juniors.numParts*idealClassSize < len(Juniors.students):
    Juniors.expandSectionsToFitStudents()
    Juniors.uplacedStudentsInRandomParts(juniors)

if Seniors.parts and Seniors.numParts*idealClassSize < len(Seniors.students):
    Seniors.expandSectionsToFitStudents()
    Seniors.uplacedStudentsInRandomParts(seniors)

total_parts = Freshmen.numParts + Sophomores.numParts + Juniors.numParts + Seniors.numParts
print("\tExpanded to",total_parts,"partitions, to fit all known students.")

# STEP-10. Append partitions to list of all Sections objects
sections = []
Freshmen.addToMainSections(sections)
Sophomores.addToMainSections(sections)
Juniors.addToMainSections(sections)
Seniors.addToMainSections(sections)

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Sort & pair teachers by comfort, making dyads ----------------------
# STEP-11. sort teachers by comfort level - unknown considered 50th percentile
# STEP-12. pair high with low teachers until all pairs formed
# == 12-A. will need to be a list of TeacherPair objects with unique IDs

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Import & clean student data from survey/ known roster ---------------
# STEP-13. Score student-votes for TeacherPairs ||2D table: [Section.id, TeacherPair.id, vote_count] *votes start with zero
# == 13-A. Totaling votes for all TeacherPairs per section (if > 0 votes)
    
# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Assign TeacherPairs to classes -------------------------------------
# == 13-B. assign TeacherPair to classes:
#     -------START repeated for all classes--------------------
# === I. highest votes in any class to identify teacherpair of interest
# == II. If no remaining votes, assign teacher-pairs arbitrarily
# = III. teacher-pair of interest then to the class with highest corresponding votes
# == IV. recalculate votes for teacher-pairs, removing assigned class
# -------END repeated for all classes--------------------

# /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\    /\  
#/  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /  \  /
#    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/    \/
#---- Export results -----------------------------------------------------
# STEP-14. output CSV files for each class, so they can be edited by hand + entered into Infinite Campus
#clear old CSV files
files = glob.glob('sections/*.csv')
for f in files:
    try:
        os.remove(f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))
#make new CSV files
for n in sections:
    filename = 'sections/#'+str(n.id)+'---grade-'+str(n.grade)+'.csv'
    grade = '' if n.grade is None else 'grade ' + str(n.grade)
    with open(filename, 'w', newline='\n') as csvfile:
        output = csv.writer(csvfile, delimiter=',')
        output.writerow(['role','id','lookupName',grade])
        for i in n.teachers: output.writerow(['teacher',i.id,findPersonByID(teachers,i.id).lookupName])
        for j in n.roster: output.writerow(['student',j.id,findPersonByID(students,j.id).lookupName])
