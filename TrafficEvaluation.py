from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import TrafficCellReaderCSV as TrafficCellReader
from DataHandler import inhabitantReaderCSV as inhabitantReader
from DataHandler import attractionReaderCSV as attractionReader
from DataHandler import cellListToJson
from DataHandler import saveTrafficCells as saveTC
from Infrastructure import ConInfrastructure as ConInfra

from collections import defaultdict


def generatePopulationGroups():
    return PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations)


def generateTrafficCells():
    trafficCellDict=defaultdict()
    trafficCellsInitDict = TrafficCellReader()#Read the traffic cells in viewing space

    for cellKey, cellName in trafficCellsInitDict.items():
        #set Name and GKZ of traffic cells an instance the object
        trafficCellDict[cellKey]=TrafficCell(cellName,cellKey)
        print(cellName)


    #---set attractivity of traffic cells
    for tc in trafficCellDict.values():
        tc.attractivity["work"] = attractionReader(tc.cellID,"work")
    #checking correct assignment
    # for tc in trafficCellDict.values():
    #     print(str(tc) + str(tc.attractivity["work"]))
    #print(str(trafficCellDict[61059].attractivity["work"]))

    #---populate TrafficCell
    inhabitantReader(trafficCellDict,"inhabitants")
    print(trafficCellDict[61059].inhabitants)

    for tc in trafficCellDict.values():
        PopulationGroup.calculatePopulation(tc)
    #PopulationGroup.calculatePopulation(trafficCellDict[61059])
    print(trafficCellDict[61059].populationParamsPerGroup)

    return trafficCellDict


def calcAllPathsForTrafficCell(trafficCellDict):
    print("Start shortest evaluation")
    for startTrafficCell in trafficCellDict.values():
        for tempCell in trafficCellDict.values():
            path = ConInfra.getShortestPaths_withStartMode(startTrafficCell.cellID, tempCell.cellID, trafficCellDict)
            startTrafficCell.shortestPaths[tempCell.cellID] = path
        print("EndCell")
    print("End shortest evaluation") 

    


def calcSimulationStep(self, parameter_list):
    pass
    
