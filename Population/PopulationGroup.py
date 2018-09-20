import time
import math
import numpy as np
from collections import defaultdict

from Population.Inhabitant import Inhabitant
from DataHandler import AttributeReaderCSV as AttributeReader
from DataHandler import behaviorReaderDummy as BehaviorReader

#--- Global Variables
gender="gender"
genderMale = "male"

#--- actual hard coded
costBudget=15.0



class PopulationGroup():

    ######################
    #--- static attributes
    ######################
    possibleAttributes={"gender":["male", "female"],
                        "agegroup":[(0,14), (15,17), (18,64), (65,100)], 
                        "employment":["employed", "unemployed"],
                        "carAviable":['aviable', 'notAviable']}
    impossibleCombinations=[((0,14),"employed"),
                            ((15,17),"employed"), 
                            ((65,100),"employed"),
                            ((0,14), 'aviable'),
                            ((15,17), 'aviable')]
    groupDict=defaultdict()

    
    ######################
    #--- methods
    ######################
    def __init__(self, groupID, attributes):
        self._attributes = attributes #dict with attributes like {"gender":"male"}
        self._groupID = groupID #Counter from 1 to 10
        #attributes for resistance
        self.k = {'cost':0.0, 'duration':1.0, 'los':0.0}
        
    
    def __str__(self):
        return str(self._attributes)

    def calcResistance(self, duration, cost, los, travelTimeBudget, costBudget, expectationLos, tripsPerDay, mode):
        if mode == 'car' and self._attributes['carAviable']!='aviable':
            return -1.0
        
        #calc duration resistance
        travelTimeBudgetPerTrip = travelTimeBudget/tripsPerDay
        resistanceDuration= math.exp((duration/travelTimeBudgetPerTrip)-1)
        #calc cost resistance
        resistanceCost = math.exp((cost/costBudget)-1)
        # calc LoS resistance
        # los is calculatet for every path in trafficCell
        # los is normed to the occupancy (occ 0.8 is approximatly los 1 ) 
        resistanceLos = los 

        resistanceSum= self.k['cost']*resistanceCost+ self.k['duration']*resistanceDuration + self.k['los']*resistanceLos

        return resistanceSum

    def calcEvaluatorGroup(self, deltaResistance):
        G=0.4
        U=0.1
        k=15
        f_0=0.2

        evGr =U + (G-U)/(1+np.exp(-deltaResistance*G*k)*(G/f_0-1))
        return evGr

        

    ############################################
    #--- static methods
    ############################################
    @staticmethod
    def calculatePopulation(trafficCell):
        #################
        # Things to Add:
        #  -car aviable?!
        ################

        if not PopulationGroup.groupDict:
            print("Groups are not generated -> genaration")
            PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations)
        ####
        #--- read all necesary Attributes
        attributesWithValues=defaultdict(dict)
        for attribute in PopulationGroup.possibleAttributes.keys():
            attributesWithValues[attribute] = AttributeReader(trafficCell.cellID,PopulationGroup, attribute)
        print(attributesWithValues)
        print(trafficCell)
        #-- traffic relevant attributes
        trafficBehaviorAttributes=["travelTimeBudget", "tripRate"]
        for attribute in trafficBehaviorAttributes:
            attributesWithValues[attribute] = BehaviorReader(attribute, PopulationGroup.possibleAttributes)
        
        ####
        #--- sample attributes for each inhabitant  ######## slow part
        time.clock()
        sampledInhabitants = []
        #set count of necessary samples
        samplecount = int(sum(attributesWithValues["agegroup"].values()))
        #calc correction for cars per inhabitant
        potantialCarUser = 0
        agegroupsChecked = set()
        for group in PopulationGroup.groupDict.values():
            if group._attributes['carAviable'] ==  PopulationGroup.possibleAttributes['carAviable'][0]:
                if  group._attributes["agegroup"] in agegroupsChecked:
                    continue
                else:                    
                    potantialCarUser += attributesWithValues["agegroup"][group._attributes['agegroup']]
                    agegroupsChecked.add(group._attributes['agegroup'])

        for i in range(0, samplecount):
            #-- generate new instance of inhabitant
            tempInhab= Inhabitant()
            #print(time.clock() - c1)
            #-- set agegroupe
                #print( attributesWithValues["agegroup"])
            
            tempInhab.setAgegroupe(i,trafficCell.inhabitants,  attributesWithValues["agegroup"], "agegroup")
            #print(time.clock() - c1)
            #-- set gender
            
            tempInhab.setGender(i,trafficCell.inhabitants,  attributesWithValues["gender"], "gender")
            #print(time.clock() - c1)
            #-- set employment
            #c1=time.clock()
            tempInhab.setEmployment(i, attributesWithValues["employment"]["employmentRate_15_64"], PopulationGroup.groupDict, "employment" , "agegroup")
            #print(time.clock() - c1)

            tempInhab.setCarAviable(i, attributesWithValues['carAviable'], PopulationGroup.groupDict, 'carAviable', 'agegroup')

            ##-- set traffic relevant attributes
            #-- set travel time budget
            #c1=time.clock()
            tempInhab.setTravelTimeBudget(i, attributesWithValues["travelTimeBudget"])
            #print(time.clock() - c1)
            #-- set number of ways
            #c1=time.clock()
            tempInhab.setTripRate(i, attributesWithValues["tripRate"])
            #print((time.clock() - c1) *trafficCell.inhabitants)

            #-- add inhabitant
            sampledInhabitants.append(tempInhab) 
            #print(str(tempInhab)  +  str(i))
            #if i > 999:            
            #     break

        #print((time.clock()-c)/(1001))
        print(time.clock())              
        print(len(sampledInhabitants))
                    
        ####
        #--- split up inhabitants to groups
        peoplePerGroupe = defaultdict(int)
        trafficParamsGroupe = defaultdict()
        for groupKey, group in PopulationGroup.groupDict.items():
            tempInhabitantList = []
            for inhab in sampledInhabitants:
                #check if inhabitant match group
                inhabitantInGroup=True
                for key in PopulationGroup.possibleAttributes.keys():
                    if group._attributes[key] != inhab.attributes[key]:
                        inhabitantInGroup=False
                        break
                
                if inhabitantInGroup:
                    tempInhabitantList.append(inhab)
            
            # set count of groupmembers
            print(group)                  
            print(len(tempInhabitantList))
            peoplePerGroupe[groupKey] = len(tempInhabitantList)            

            # set params for group
            timebudget=None
            tripRate= None
            for inhab in tempInhabitantList:
                if timebudget == None or tripRate == None:
                    timebudget = inhab.travelTimeBudget
                    tripRate = inhab.tripRate
                else:
                    timebudget = timebudget + inhab.travelTimeBudget
                    tripRate = tripRate + inhab.tripRate

            timebudget = timebudget/float(peoplePerGroupe[groupKey])
            tripRate = tripRate/float(peoplePerGroupe[groupKey])
            #print(timebudget)
            #print(tripRate)
            

            trafficParamsGroupe[groupKey]={"travelTimeBudget":timebudget, "tripRate" : tripRate, "costBudget": costBudget}

        trafficCell.SetPopulationGroups(peoplePerGroupe)
        trafficCell.SetPopulationParams(trafficParamsGroupe)



    @staticmethod
    def generateGroups(possibleAttributes,impossibleCombinations):
        #generate a list with all possible attribute combinations
        attributeList=[]
        attributeNameList=[] 
        for key, value in possibleAttributes.items():
            attributeList.append(value) 
            attributeNameList.append(key)

        #print(attributeList[0])
        poplist=[]
        for attribute in attributeList[0]:
            poplist.append((attribute,))
        #print(poplist)

        toAdd =  attributeList
        toAdd.pop(0)      
        for arg in toAdd:            
            poplist = [(*pop, attribute) for pop in poplist for attribute in arg]       
        
        #remove combinations, witch are listed in impossibleCombinations
        tempSet = set()
        for group in poplist:
            for att1,att2 in impossibleCombinations:
                if (att1 in group) and (att2 in group):                    
                    tempSet.add(group)

        poplist = [gr for gr in poplist if gr not in tempSet]


        #genarate a list of objects for the groups        
        for idx, group in enumerate(poplist): #enumerate to generate a idividual ID
            print(dict(zip(attributeNameList,group)))
            keystring='popGroup' + str(idx)
            print(keystring)
            PopulationGroup.groupDict[keystring]=(PopulationGroup(idx,dict(zip(attributeNameList,group))))



        #print(poplist)           
        return PopulationGroup.groupDict
    





        
