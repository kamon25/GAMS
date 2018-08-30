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
    print("Start path evaluation")
    for startTrafficCell in trafficCellDict.values():
        for tempCell in trafficCellDict.values():
            path = ConInfra.getShortestPaths_withStartMode(startTrafficCell.cellID, tempCell.cellID, trafficCellDict)
            startTrafficCell.shortestPaths[tempCell.cellID] = path
            #print(path)
        print("Kürzeste Wege der Gemeinde:" + str(startTrafficCell._name))
    print("End path evaluation") 

    
def choseDestinationAndMode(trafficCellDict, purposForJourney):
    tripsPerDay=3.4  ############### subsitute with Data !!!
    
    for trafficCell in trafficCellDict.values():
        #calc demand for each populationGroup in each trafficCell
        trafficDemandPerGroup={(popGroup):(count if popGroup._attributes["employment"]==PopulationGroup.possibleAttributes["employment"][0] else 0) 
                                for popGroup, count in trafficCell.popPerGroup.items()}
              
        trafficDemandPerGroup = {(popGroup):(demand*trafficCell.populationParamsPerGroup[popGroup]['tripRate']) for popGroup, demand in trafficDemandPerGroup.items()}

       
        #calc ratio attractivity to resistance und sum for each popGroup
        ratioAttractivityResistance=defaultdict()   # {destination:{mode:{group: ratio}}}     
        sumRatio=defaultdict(float) #{popGroup: sumRatio}

        for destination, modes in trafficCell.connectionParams.items():
            modeRatio = defaultdict() #{mode: {group: ratio }}
            for mode, connectionParams in modes.items():
                groupRatio=defaultdict()
                for popGroup, popParams in trafficCell.populationParamsPerGroup.items():
                    resistance=popGroup.calcResistance(connectionParams['duration'], connectionParams['cost'], 1,
                                                        popParams['travelTimeBudget'],
                                                        popParams['costBudget'], 1, tripsPerDay) #1 have to be reset with LoS 
                    attract= trafficCellDict[destination].attractivity[purposForJourney]
                    tempRatio=attract/resistance
                    sumRatio[popGroup] += tempRatio
                    groupRatio[popGroup] = tempRatio
                modeRatio[mode] = groupRatio
            ratioAttractivityResistance[destination]=modeRatio

        # calcGroupPart for purpose destination mode
        groupPartDesMode=defaultdict()  # {destination:{mode:{group: numberOfrides}}} 

        for destination, modes in ratioAttractivityResistance.items():
            modeGroupPart = defaultdict()
            for mode, groups in modes.items():
                groupPart=defaultdict()
                for group, ratio in groups.items():
                    groupPart[group]=(ratio/sumRatio[group])*trafficDemandPerGroup[group]
                modeGroupPart[mode]=groupPart
            groupPartDesMode[destination]=modeGroupPart
        
        trafficCell.purposeSestinationModeGroup[purposForJourney]=groupPartDesMode

      


def calcSimulationStep(self, parameter_list):
    pass
    