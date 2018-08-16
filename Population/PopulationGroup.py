from collections import defaultdict
from Population.Inhabitant import Inhabitant
from DataHandler import AttributeReaderCSV as AttributeReader
from DataHandler import behaviorReaderDummy as BehaviorReader

#--- Global Variables
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

        if not PopulationGroup.grouplist:
            print("Groups are not generated -> genaration")
            PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations)
        
        #--- read all necesary Attributes
        attributesWithValues=defaultdict(dict)
        for attribute in PopulationGroup.possibleAttributes.keys():
            attributesWithValues[attribute] = AttributeReader(trafficCell.cellID,PopulationGroup, attribute)
        print(attributesWithValues)
        #-- traffic relevant attributes
        trafficBehaviorAttributes=["travelTimeBudget"]
        for attribute in trafficBehaviorAttributes:
            attributesWithValues[attribute] = BehaviorReader(attribute, PopulationGroup.possibleAttributes)

        #--- sample attributes for each inhabitant 
        sampledInhabitants = []
        for i in range(0, trafficCell.inhabitants):
            #-- generate new instance of inhabitant
            tempInhab= Inhabitant()
            #-- set agegroupe
                #print( attributesWithValues["agegroup"])
            tempInhab.setAgegroupe(i,trafficCell.inhabitants,  attributesWithValues["agegroup"])
            #-- set gender
            tempInhab.setGender(i,trafficCell.inhabitants,  attributesWithValues["gender"])
            #-- set employment
            tempInhab.setEmployment(i, attributesWithValues["employmentRate_15_64"], PopulationGroup.grouplist.copy())

            ##-- set traffic relevant attributes

            #-- set travel time budget

            ################
            #CONTINUE HERE
            ################




            #-- add inhabitant
            sampledInhabitants.append(tempInhab)
            print(tempInhab.agegroupe)
            print(tempInhab.gender)
            print(tempInhab.employment)
            break

         
            

        

        




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
        
