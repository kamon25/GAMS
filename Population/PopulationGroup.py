class PopulationGroup():

    def __init__(self, name, gender,agegroup, employment, carAviable, averageIncome, paramsChoice):
        self._name=name
        self.__gender=gender #male or female
        self.__agegroup=agegroup 
        self.__employment=employment #yes or no 
        self.__carAviable=carAviable
        self.__averageIncome=averageIncome
        self.__paramsChoice=paramsChoice
        self._timebudget = None
        
    
    
    @staticmethod
    def calculatePopulation(populationParams):
        pass
    
    
        
