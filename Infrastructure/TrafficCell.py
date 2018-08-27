import pandas as pd 
import numpy as np
from collections import defaultdict 



class TrafficCell():

    def __init__(self, name, cellID):
        self._name=name
        self.inhabitants=int()
        self.popPerGroup=None       #dict with {PopulationGroup : count}
        self.cellID=cellID        

        self.populationParamsPerGroup=None #dict with {PopulationGroup : {travelTimeBudget: int, tripRate : int}}
        self.attractivity=defaultdict()
        
        self.shortestPaths=defaultdict()    
    
    def __str__(self):
        return str(self._name)   

    def SetPopulationParams(self,populationParams):
        self.populationParamsPerGroup=populationParams

    def SetPopulationGroups(self, popGroups):
        self.popPerGroup=popGroups
    
    ### preparing dicts for encoding to json
    def toDict(self):
        tempDict={'name':self._name, 'inhabitants': self.inhabitants}
        return tempDict
    
    def toDictWithPopGroupe(self):
        popGroupDict=defaultdict()

        for group, count in self.popPerGroup.items():
            groupid = "bhg" + str(group._groupID)
            popGroupAttributeDict={}
            popGroupAttributeDict["inhabitants"] = count
            popGroupDict[groupid]=popGroupAttributeDict
            
        tempDict={'name':self._name, 'inhabitants': self.inhabitants, "inhabitantGroups": popGroupDict}
        
        return tempDict




