from objects import *

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

#school email to lookupname
def lookupNameFromFirstLast(first,last):
    name = first + last
    return name.lower()

def surname(name):
        arr = name.split(' ')
        for name in arr:
            if name is not None: sur_name = name    
        return sur_name.lower()

def lastNameBool(students, requestor, requestee):
    id = findIDByLastName(students, requestor, requestee)
    if id: return True
    return False

def findIDByLastName(students, requestor, requestee):
    found_count = 0
    result = 0
    for stu in students:
        if requestee and requestee == stu.surname and requestor.grade == stu.nextGrade:
            # print(requestor.lookupName,'in grade',str(requestor.grade),'asked for',requestee,'in grade',str(stu.nextGrade))
            found_count += 1
            result = stu.id
    if found_count == 1: return result

def emailFromFirstLast(firstName,lastName):
    return (lastName+'.'+firstName+'@madisonps.org').lower()
