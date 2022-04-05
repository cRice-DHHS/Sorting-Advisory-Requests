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
