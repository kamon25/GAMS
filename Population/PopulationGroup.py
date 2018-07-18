import itertools


class PopulationGroup():

    #static attributes
    possibleGender = ["male", "female"]
    possibleAgegroups = [(6,14), (15,19), (20,65), (65,100)]
    possibleEmploymentState= ["employed", "unemployed"]
    groupAttributesNames=("gender", "age", "employment")
    impossibleCombinations=[(possibleAgegroups[0],possibleEmploymentState[0]), 
                            (possibleAgegroups[1],possibleEmploymentState[0]),
                            (possibleAgegroups[3],possibleEmploymentState[0])]
    
    #static methods
    @staticmethod
    def calculatePopulation(populationParams):
        pass
    
    @staticmethod
    def generateGroups(impossibleCombinations,groupAttributesNames ,*args):
        #generate a list with all possible attribute combinations
        poplist = [[arg] for arg in args[0]]
        toAdd =  list(args)
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
            grouplist.append(PopulationGroup(group))
                   
        return grouplist
    


    def __init__(self, attributes):
        self.__attributes = attributes
        self.__paramsChoice={}
    
    def __str__(self):
        # output = None
        # output= output + str(att) for att in self.__attributes)
        # return output
        return "test"
        
