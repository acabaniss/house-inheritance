"""Example script for using households. Realistic data import
Created on Tue Apr  7 22:26:25 2020

@author: acabaniss




"""
#Import the households package
import numpy as np
import random as rd
import pandas
import os
import matplotlib.pyplot as plt
#os.chdir('..')
import households
from households import behavior


male, female = (households.male,households.female)
###REALISTIC RUNS
#Life tables are Coale and Demeny: Male, west 4, female west 2, .2% annual increase. See Bagnall and frier
maledeath = pandas.read_csv('../data/demo/West4Male.csv')
ages = list(maledeath.Age1) + [list(maledeath.Age2)[-1]]
malerates = list(maledeath[maledeath.columns[2]])
femaledeath = pandas.read_csv('../data/demo/West2Female.csv')
femalerates = list(femaledeath[femaledeath.columns[2]])
age_list = list([0,1]+[x for x in range(5,105,5)])
bagnallfrier = households.AgeTable(ages = age_list , sex1 = male, rates1 = malerates, sex2 = female, rates2 = femalerates)
del maledeath, femaledeath

examplebirth = households.AgeTable([0,12,40,50,100],female,[0,.3,.1,0],male,[0,0,0,0,0])

examplemarriage = households.AgeTable([0,12,17,100],female,[0,1./7.5,1./7.5],male,[0,0,0.0866]) #These values based on Bagnall and Frier, 113-4 (women) and 116 (men) for Roman egypt

def find_heirs_moderate_inheritance(person):
    """
    Upon the death of the patriarch, the house is given to someone in this
    order:
        
    Male children in order of age
    Children of brothers not in line for succession (have to move into household)
    
    This stems from the description of the moderate inheritance regime in Asheri
    """
    #The moderate inheritance regime of Asheri 1963
    # Check if patriarch
    sons = behavior.inheritance.find_heirs_sons_oldest_to_youngest(person)
    brotherssons = behavior.inheritance.find_heirs_brothers_sons_oldest_to_youngest(person)
    return [sons,brotherssons]

inheritance_moderate = behavior.inheritance.InheritanceRuleComplex(has_property = behavior.inheritance.has_property_houses,
                                                                   find_heirs = find_heirs_moderate_inheritance,
                                                                   limit_heirs = behavior.inheritance.limit_heirs_not_owners,
                                                                   distribute_property = behavior.inheritance.distribute_property_to_first_heir_and_move_household,
                                                                   failure = behavior.inheritance.failed_inheritance_no_owner)
                
def brother_loses_out_15(house):
    """Fragmentation rule with age of majority 15.
    
    """
    if house.people != [] and house.owner != None:
        households.behavior.fragmentation.brother_loses_out(house,15)
            
#An example of a single realistic run
np.random.seed(505401)
testcase = households.Community(name = 'EgyptianVillage',pop = 500,area = 500,startage = 12, mortab = bagnallfrier,marrtab = examplemarriage,birthtab = examplebirth,locality = households.behavior.locality.patrilocality,inheritance =  inheritance_moderate,fragmentation = brother_loses_out_15)

#Lets progress this 100 years
for y in range(100):
    testcase.progress()

plt.hist([x.age for x in testcase.people])
plt.plot(range(testcase.year+1),testcase.poplist)
plt.hist([len(h.people) for h in testcase.houses],bins=range(20))

#Pick a random occupied house
h = rd.choice([h for h in testcase.houses if len(h.people)>1])
print(households.narrative.census(h))
for x in h.people:
    print(households.narrative.biography(x))