from collections import defaultdict
from Population.Inhabitant import Inhabitant
from DataHandler import AttributeReaderCSV as AttributeReader
from DataHandler import behaviorReaderDummy as BehaviorReader

#--- Global Variables
gender="gender"
genderMale = "male"



class PopulationGroup():

    #--- static attributes
    possibleAttributes={"gender":["male", "female"],
                        "agegroup":[(0,14), (15,59), (60,100)], 
                        "employment":["employed", "unemployed"]}
    impossibleCombinations=[((0,14),"employed"), 
                            ((60,100),"employed")]
    grouplist=[]
    
    #--- static methods
    @staticmethod
    def calculatePopulation(trafficCell):
        #################
        # Things to Add:
        #  -car aviable?!
        ################

        if not PopulationGroup.grouplist:
            print("Groups are not generated -> genaration")
            PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations)
        ################################
        #--- read all necesary Attributes
        attributesWithValues=defaultdict(dict)
        for attribute in PopulationGroup.possibleAttributes.keys():
            attributesWithValues[attribute] = AttributeReader(trafficCell.cellID,PopulationGroup, attribute)
        print(attributesWithValues)
        #-- traffic relevant attributes
        trafficBehaviorAttributes=["travelTimeBudget", "tripRate"]
        for attribute in trafficBehaviorAttributes:
            attributesWithValues[attribute] = BehaviorReader(attribute, PopulationGroup.possibleAttributes)
        
        ########################################
        #--- sample attributes for each inhabitant 
        sampledInhabitants = []
        for i in range(0, trafficCell.inhabitants):
            #-- generate new instance of inhabitant
            tempInhab= Inhabitant()
            #-- set agegroupe
                #print( attributesWithValues["agegroup"])
            tempInhab.setAgegroupe(i,trafficCell.inhabitants,  attributesWithValues["agegroup"], "agegroup")
            #-- set gender
            tempInhab.setGender(i,trafficCell.inhabitants,  attributesWithValues["gender"], "gender")
            #-- set employment
            tempInhab.setEmployment(i, attributesWithValues["employmentRate_15_64"], PopulationGroup.grouplist.copy(), "employment" , "agegroup")

            ##-- set traffic relevant attributes
            #-- set travel time budget
            tempInhab.setTravelTimeBudget(i, attributesWithValues["travelTimeBudget"])
            #-- set number of ways
            tempInhab.setTripRate(i, attributesWithValues["tripRate"])


            #-- add inhabitant
            sampledInhabitants.append(tempInhab) 
            # if i > 10:
            #     break
                      

                    
        ########################################
        #--- split up inhabitants to groups
        peoplePerGroupe = defaultdict(int)
        trafficParamsGroupe = defaultdict()
        for group in PopulationGroup.grouplist:
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
            print(group)                    ################################################ CONTINUE DEBUGUNG HERE
            print(len(tempInhabitantList))
            peoplePerGroupe[group] = len(tempInhabitantList)            

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
            print(timebudget)
            print(tripRate)
            timebudget = timebudget/float(peoplePerGroupe[group])
            tripRate = tripRate/float(peoplePerGroupe[group])
            

            trafficParamsGroupe[group]={"travelTimeBudget":timebudget, "tripRate" : tripRate}

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
        for group in poplist:
            for att1,att2 in impossibleCombinations:
                if (att1 in group) and (att2 in group):                    
                    poplist.remove(group)

        #genarate a list of objects for the groups
        
        for group in poplist:
            #print(dict(zip(attributeNameList,group)))
            PopulationGroup.grouplist.append(PopulationGroup(dict(zip(attributeNameList,group))))

        #print(poplist)           
        return PopulationGroup.grouplist
    


    def __init__(self, attributes):
        self._attributes = attributes #dict with attributes like {"gender":"male"}
        self.__paramsChoice={}
    
    def __str__(self):
        return str(self._attributes)
        
