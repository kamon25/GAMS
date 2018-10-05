import pandas as pd
import numpy as np
from collections import defaultdict

from Infrastructure import ConInfrastructure as ConInfra


class TrafficCell():

    def __init__(self, name, cellID):
        self._name = name
        self.cellID = cellID
        self.inhabitants = int()
        self.inhabitantForecast = defaultdict() # dict {year: inhabitants}
        self.popPerGroup = None  # dict with {PopulationGroupKey : count}
        

        # dict with {PopulationGroupKey : {travelTimeBudget: int, tripRate : int, tripRateWork: int, costBudget : float}}
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

    def toDictWithPopGroup(self):
        popGroupDict = defaultdict()

        for groupKey, count in self.popPerGroup.items():
            popGroupAttributeDict = {}
            popGroupAttributeDict["inhabitants"] = count
            popGroupDict[groupKey] = popGroupAttributeDict

        tempDict = {'name': self._name, 'inhabitants': self.inhabitants,
                    "populationGroups": popGroupDict}

        return tempDict

    def calcConnectionParams(self, carCostKm, ptCostZone, jsonParameter):
        distanceInZone = jsonParameter['averageDistanceInCell']
        speedInZoneCar = jsonParameter['speedInZoneCar']
        speedInZonePT = jsonParameter['speedInZonePT']

        for destination, modes in self.pathConnectionList.items():
            modeParams = defaultdict()

            for mode, path in modes.items():
                # calc attributes from distance and zones
                copypath = path.copy() 
                if copypath:     
                    distance =0
                    time = 0
                    cost = 0
                    zoneCounter = 0
                    los = 1
                    for connection in copypath:
                        distance += connection.distance
                        time += connection.distance/connection.averageSpeedZero
                        if connection.mode== 'car':
                            cost += connection.distance*carCostKm
                            zoneCounter = 0
                        elif mode == 'publicTransport':
                            cost += ptCostZone[zoneCounter]
                            zoneCounter += 1
                else:
                    los = 1
                    zoneCounter=0
                    distance=distanceInZone
                    if mode == 'car':
                        time = distance/speedInZoneCar
                        cost = distance*carCostKm
                        
                    elif mode == 'publicTransport':
                        time = distance/speedInZonePT
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

    def updateInhabitants(self, year):
        oldInhabitants = self.inhabitants
        oldPopGroups = self.popPerGroup
        ihForecast = self.inhabitantForecast

        # calc new inhabitants
        newInhabitants = int()

        #Interpolate Inhabitants or return if out of range
        if year in ihForecast:
            newInhabitants = ihForecast[year]
        elif year <  min(ihForecast):
            return
        elif year > max(ihForecast):
            return
        else:
            forecastYears=sorted(list(ihForecast.keys()))
            forecastInhabitants=list()
            for y in forecastYears:
                forecastInhabitants.append(ihForecast[y])

            newInhabitants = np.interp(year,forecastYears, forecastInhabitants)

        self.inhabitants = newInhabitants
        for popGroup, count in oldPopGroups.items():
            self.popPerGroup[popGroup] = int(count*(float(newInhabitants)/float(oldInhabitants)))

    ###########################
    #
    #   Methods for intern use (validation)

    def printEmployed(self, groupDict):
        sumEmployed=0
        for groupkey, group in groupDict.items():
            if group._attributes["employment"] == "employed":
                sumEmployed += self.popPerGroup[groupkey]
        
        print(self._name  + " Employed: " + str(sumEmployed))
