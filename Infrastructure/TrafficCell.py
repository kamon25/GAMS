import pandas as pd 
import numpy as np
from collections import defaultdict 

from Infrastructure import ConInfrastructure as ConInfra

class TrafficCell():

    def __init__(self, name, cellID):
        self._name=name
        self.inhabitants=int()
        self.popPerGroup=None       #dict with {PopulationGroupKey : count}
        self.cellID=cellID        

        self.populationParamsPerGroup=None #dict with {PopulationGroupKey : {travelTimeBudget: int, tripRate : int, costBudget : float}}
        self.attractivity=defaultdict()     #{purpose: attractivity}
        
        self.shortestPaths=defaultdict()    #{targetCell: {mode:[(start, connectionType, dist),(start,...)]}}
        self.pathConnectionList=defaultdict() #{targetCell: {mode:{list of connections}}}
        self.connectionParams = defaultdict() #{'duration': time, 'cost': cost, 'distance': distance}

        self.purposeSestinationModeGroup=defaultdict() #{Purpose{destination: { mode:{popGroup: trips}}}}
    
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

        for groupKey, count in self.popPerGroup.items():
            popGroupAttributeDict={}
            popGroupAttributeDict["inhabitants"] = count
            popGroupDict[groupKey]=popGroupAttributeDict
            
        tempDict={'name':self._name, 'inhabitants': self.inhabitants, "populationGroups": popGroupDict}
        
        return tempDict
    
    def calcConnectionParams(self, carCostKm, ptCostZone):
        
        for destination, modes in self.shortestPaths.items():
            modeParams=defaultdict()
            for mode, path in modes.items():

                #calc attributes from distance and zones               
                copypath = path.copy()
                copypath.pop()
                distance = 0
                time = 0
                cost = 0
                zoneCounter = 0
                for _, connection, dis in copypath:
                    distance+=dis
                    time += dis*ConInfra.costModes[connection]
                    if connection.split('_')[0]=='car':
                        cost += dis*carCostKm
                        zoneCounter=0
                    else:
                        cost += ptCostZone[zoneCounter]
                        zoneCounter += 1   

                params={'duration': time, 'cost': cost, 'distance': distance}
                
                modeParams[mode]=params
            self.connectionParams[destination]=modeParams
        
            




        




