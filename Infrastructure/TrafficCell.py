import pandas as pd
import numpy as np
from collections import defaultdict

from Infrastructure import ConInfrastructure as ConInfra


class TrafficCell():

    def __init__(self, name, cellID):
        self._name = name
        self.inhabitants = int()
        self.popPerGroup = None  # dict with {PopulationGroupKey : count}
        self.cellID = cellID

        # dict with {PopulationGroupKey : {travelTimeBudget: int, tripRate : int, costBudget : float}}
        self.populationParamsPerGroup = None
        self.attractivity = defaultdict()  # {purpose: attractivity}

        # {targetCell: {mode:[(start, connectionType, dist),(start,...)]}}
        self.shortestPaths = defaultdict()
        # {targetCell: {mode:[list of connections]}}
        self.pathConnectionList = defaultdict()
        # {'duration': time, 'cost': cost, 'distance': distance}
        self.connectionParams = defaultdict()

        # {Purpose{destination: { mode:{popGroup: trips}}}}
        self.purposeSestinationModeGroup = defaultdict()
        # {Purpose{destination: { mode:trips}}}
        self.purposeDestinationMode = defaultdict()
         # expected LoS per group
        self.expectedResistance=defaultdict() # {Purpose{destination: { mode:{ popGroup: excpectedLoS}}}}

    def __str__(self):
        return str(self._name)

    def SetPopulationParams(self, populationParams):
        self.populationParamsPerGroup = populationParams

    def SetPopulationGroups(self, popGroups):
        self.popPerGroup = popGroups
    

    # preparing dicts for encoding to json
    def toDict(self):
        tempDict = {'name': self._name, 'inhabitants': self.inhabitants}
        return tempDict

    def toDictWithPopGroupe(self):
        popGroupDict = defaultdict()

        for groupKey, count in self.popPerGroup.items():
            popGroupAttributeDict = {}
            popGroupAttributeDict["inhabitants"] = count
            popGroupDict[groupKey] = popGroupAttributeDict

        tempDict = {'name': self._name, 'inhabitants': self.inhabitants,
                    "populationGroups": popGroupDict}

        return tempDict

    def calcConnectionParams(self, carCostKm, ptCostZone):
        distanceInZone =1

        for destination, modes in self.shortestPaths.items():
            modeParams = defaultdict()

            for mode, path in modes.items():
                # calc attributes from distance and zones
                copypath = path.copy()
                copypath.pop()   
                if copypath:     
                    distance =0
                    time = 0
                    cost = 0
                    zoneCounter = 0
                    los = 1
                    for _, connection, dis in copypath:
                        distance += dis
                        # check Time calculation
                        time += dis*ConInfra.costModes[connection]
                        if connection.split('_')[0] == 'car':
                            cost += dis*carCostKm
                            zoneCounter = 0
                        else:
                            cost += ptCostZone[zoneCounter]
                            zoneCounter += 1
                else:
                    los = 1
                    zoneCounter=0
                    distance=distanceInZone
                    if mode == 'car':
                        time = distance*ConInfra.costModes['car_countryroad']
                        cost = distance*carCostKm
                        
                    elif mode == 'publicTransport':
                        time = distance*ConInfra.costModes['publicTransport_bus']
                        cost = ptCostZone[zoneCounter]    

                params = {'duration': time, 'cost': cost,
                          'distance': distance, 'los': los}

                modeParams[mode] = params
            self.connectionParams[destination] = modeParams

    def updateConnectionParams(self):

        for destination, modes in self.pathConnectionList.items():
            for mode, pathList in modes.items():
                
                sumDistance = 0
                los = 0
                if pathList:
                    for con in pathList:
                        sumDistance += con.distance
                        los += con.distance*con.currentLos
                else:
                    sumDistance=1
                    los=1


                # calc weighted average
                averageLos = los/float(sumDistance)
                self.connectionParams[destination][mode]['los'] = averageLos
