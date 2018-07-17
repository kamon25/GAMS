class PopulationGroup():

    posibleGender = ["male", "female"]
    posibleAgegroups = [[6,14], [15,19], [20,65], [65,100] ]
    

    def __init__(self, name, gender,agegroup, employment, carAviable, averageIncome, timebudget, paramsChoice):
        self._name=name
        self.__gender=gender #male or female
        self.__agegroup=agegroup 
        self.__employment=employment #yes or no 
        self.__carAviable=carAviable
        self.__averageIncome=averageIncome
        self.__paramsChoice=paramsChoice
        self._timebudget = timebudget
        
    
    
    @staticmethod
    def calculatePopulation(populationParams):
        pass
    
    @staticmethod
    def generateGroups():
        poblist=[]
        for gen in PopulationGroup.posibleGender:
            for age in PopulationGroup.posibleAgegroups:
                poblist.append([gen, age])


        
