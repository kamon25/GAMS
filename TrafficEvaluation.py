from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import TrafficCellReaderCSV as TrafficCellReader
from DataHandler import inhabitantReaderCSV as inhabitantReader
from DataHandler import attractionReaderCSV as attractionReader
from DataHandler import cellListToJson
from DataHandler import resultPerStepInFolders
from DataHandler import creatSimConfigFile
from DataHandler import saveTrafficCells as saveTC
from Infrastructure import ConInfrastructure as ConInfra

from collections import defaultdict


def generatePopulationGroups():
    return PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations)


def generateTrafficCells():
    trafficCellDict = defaultdict()
    # Read the traffic cells in viewing space
    trafficCellsInitDict = TrafficCellReader()

    for cellKey, cellName in trafficCellsInitDict.items():
        # set Name and GKZ of traffic cells an instance the object
        trafficCellDict[cellKey] = TrafficCell(cellName, cellKey)
        print(cellName)

    # ---set attractivity of traffic cells
    for tc in trafficCellDict.values():
        tc.attractivity["work"] = attractionReader(tc.cellID, "work")
    # checking correct assignment
    # for tc in trafficCellDict.values():
    #     print(str(tc) + str(tc.attractivity["work"]))
    # print(str(trafficCellDict[61059].attractivity["work"]))

    # ---populate TrafficCell
    inhabitantReader(trafficCellDict, "inhabitants")
    print(trafficCellDict['61059'].inhabitants)

    for tc in trafficCellDict.values():
        PopulationGroup.calculatePopulation(tc)
    # PopulationGroup.calculatePopulation(trafficCellDict[61059])
    print(trafficCellDict['61059'].populationParamsPerGroup)

    return trafficCellDict


def calcAllPathsForTrafficCell(trafficCellDict):
    print("Start path evaluation")
    for startTrafficCell in trafficCellDict.values():
        for tempCell in trafficCellDict.values():
            path, connections = ConInfra.getShortestPaths_withStartMode(
                startTrafficCell.cellID, tempCell.cellID, trafficCellDict)
            startTrafficCell.shortestPaths[tempCell.cellID] = path
            startTrafficCell.pathConnectionList[tempCell.cellID] = connections

            # print(path)
        print("Kürzeste Wege der Gemeinde:" + str(startTrafficCell._name))
    print("End path evaluation")


def choseDestinationAndMode(trafficCellDict, groupDict, purposForJourney, step):
    tripsPerDay = 3.4  # subsitute with Data !!!

    for trafficCell in trafficCellDict.values():
        # calc demand for each populationGroup in each trafficCell

        trafficDemandPerGroup = {(popGroupKey): (count if groupDict[popGroupKey]._attributes["employment"] == PopulationGroup.possibleAttributes["employment"][0] else 0)
                                 for popGroupKey, count in trafficCell.popPerGroup.items()}

        trafficDemandPerGroup = {(popGroupKey): (
            demand*trafficCell.populationParamsPerGroup[popGroupKey]['tripRate']) for popGroupKey, demand in trafficDemandPerGroup.items()}

        # calc ratio attractivity to resistance und sum for each popGroup
        # {destination:{mode:{group: ratio}}}
        ratioAttractivityResistance = defaultdict()
        sumRatio = defaultdict(float)  # {popGroup: sumRatio}

        for destination, modes in trafficCell.connectionParams.items():
            modeRatio = defaultdict()  # {mode: {group: ratio }}
            for mode, connectionParams in modes.items():
                groupRatio = defaultdict()
                for popGroupKey, popParams in trafficCell.populationParamsPerGroup.items():
                    resistance = groupDict[popGroupKey].calcResistance(connectionParams['duration'], connectionParams['cost'], 1,
                                                                       popParams['travelTimeBudget'],
                                                                       popParams['costBudget'], 1, tripsPerDay)  # 1 have to be reset with LoS
                    attract = trafficCellDict[destination].attractivity[purposForJourney]
                    tempRatio = attract/resistance
                    sumRatio[popGroupKey] += tempRatio
                    groupRatio[popGroupKey] = tempRatio
                modeRatio[mode] = groupRatio
            ratioAttractivityResistance[destination] = modeRatio

        # calcGroupPart for purpose destination mode
        groupPartDesMode = defaultdict()  # {destination:{mode:{group: trips}}}
        # add sums for modes {destination:{mode: trips}}
        desModeTrips = defaultdict()

        for destination, modes in ratioAttractivityResistance.items():
            modeGroupPart = defaultdict()
            modeTrips = defaultdict()
            for mode, groups in modes.items():
                groupPartDemand = defaultdict()
                sumTripsPerMode = 0
                for group, ratio in groups.items():
                    groupPartDemand[group] = (
                        ratio/sumRatio[group])*trafficDemandPerGroup[group]
                    sumTripsPerMode += groupPartDemand[group]
                modeGroupPart[mode] = groupPartDemand
                modeTrips[mode] = sumTripsPerMode
                # add load to the connections of the shortest paht
                for connection in trafficCell.pathConnectionList[destination][mode]:
                    connection.setStepLoad(sumTripsPerMode, step)

            groupPartDesMode[destination] = modeGroupPart
            desModeTrips[destination] = modeTrips

        trafficCell.purposeSestinationModeGroup[purposForJourney] = groupPartDesMode
        trafficCell.purposeDestinationMode[purposForJourney] = desModeTrips


def calcSimulationStep(trafficCellDict, groupDict, step):

    choseDestinationAndMode(trafficCellDict, groupDict, 'work', step)


def runSimulation(trafficCellDict, groupDict, years):
    stepsPerYear = 6
    listOfFiles = []
    steps = years*stepsPerYear

    # {timestep:{startCell:{Purpose{destination: { mode:{popGroup: trips}}}}
    resultOfSimulation = defaultdict()

    for st in range(0, steps):
        # MAIN Calculation
        calcSimulationStep(trafficCellDict, groupDict, st)
        # write values
        startCellDict = defaultdict()
        for cellKey, cell in trafficCellDict.items():
            startCellDict[cellKey] = dict([('Sum_Trips_per_Mode', cell.purposeDestinationMode),
                                           ('Trips_per_group', cell.purposeSestinationModeGroup)])
            # startCellDict[cellKey]=cell.purposeSestinationModeGroup

        # Save results of simulation stepwise in JSON and get the list of Filenames
        listOfFiles.append(resultPerStepInFolders(startCellDict, st))
        # Save result of simulation in Dict
        resultOfSimulation[st] = startCellDict

        if st % stepsPerYear == 0:
            print("year: " + str(st/stepsPerYear))

    # Config for visualisation
    creatSimConfigFile('1', listOfFiles, steps)

    return resultOfSimulation
