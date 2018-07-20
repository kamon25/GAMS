import itertools


class PopulationGroup():

    #static attributes

    possibleAttributes={"gender":["male", "female"],
                        "agegroup":[(6,14), (15,19), (20,65), (65,100)], 
                        "employment":["employed", "unemployed"]}
    impossibleCombinations=[((6,14),"employed"), 
                            ((15,19),"employed"),
                            ((65,100),"employed")]
    
    #static methods
    @staticmethod
    def calculatePopulation(populationParams):
        pass
    
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
        grouplist=[]
        for group in poplist:
            #print(dict(zip(attributeNameList,group)))
            grouplist.append(PopulationGroup(dict(zip(attributeNameList,group))))

        #print(poplist)           
        return grouplist
    


    def __init__(self, attributes):
        self.__attributes = attributes #dict with attributes like {"gender":"male"}
        self.__paramsChoice={}
    
    def __str__(self):
        return str(self.__attributes)
        
