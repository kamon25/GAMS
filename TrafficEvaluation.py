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


def generatePopulationGroups(jsonParameter):
    return PopulationGroup.generateGroups(PopulationGroup.possibleAttributes, PopulationGroup.impossibleCombinations, jsonParameter)


def generateTrafficCells(jsonParameter):
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
        PopulationGroup.calculatePopulation(tc,jsonParameter)
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

######################
#
# Methods for a smulation step
#
######################


def choseDestinationAndMode(trafficCellDict, groupDict, purposForJourney, step, jsonParameter):
    #weight for exponational smoothing in resistance forecasting
    weightSmoothing=jsonParameter["weight_smoothing"]
    ratioToIntern = 1.0 - jsonParameter["ratioToExtern"]


    for trafficCell in trafficCellDict.values():
        # calc demand for each populationGroup in each trafficCell

        trafficDemandPerGroup = {(popGroupKey): (count* ratioToIntern if groupDict[popGroupKey]._attributes["employment"] == PopulationGroup.possibleAttributes["employment"][0] else 0)
                                 for popGroupKey, count in trafficCell.popPerGroup.items()}

        trafficDemandPerGroup = {(popGroupKey): (
            demand*trafficCell.populationParamsPerGroup[popGroupKey]['tripRateWork']) for popGroupKey, demand in trafficDemandPerGroup.items()}

        # calc ratio attractivity to resistance und sum for each popGroup
        # {destination:{mode:{group: ratio}}}
        ratioAttractivityResistance = defaultdict()
        sumRatio = defaultdict(float)  # {popGroup: sumRatio}
        # {destination:{mode:{group: resistance}}}
        expextedResistanceDesModeGroup = defaultdict()
        deltaResistanceDesModeGroup = defaultdict()

        for destination, modes in trafficCell.connectionParams.items():
            modeRatio = defaultdict()  # {mode: {group: ratio }}
            expextedResistanceModeGroup= defaultdict()
            deltaResistanceModeGroup=defaultdict()
            for mode, connectionParams in modes.items():
                groupRatio = defaultdict()
                expextedResistanceGroup= defaultdict()
                deltaResistanceGroup=defaultdict()
                for popGroupKey, popParams in trafficCell.populationParamsPerGroup.items():
                    #calcResistance
                    resistance = groupDict[popGroupKey].calcResistance(connectionParams['duration'], connectionParams['cost'], connectionParams['los'],
                                                                       popParams['travelTimeBudget'],
                                                                       popParams['costBudget'], 1, trafficCell.populationParamsPerGroup[popGroupKey]['tripRate'], mode,jsonParameter)  # 1 have to be reset with LoS
                    if resistance == - 1.0:
                        groupRatio[popGroupKey] = 0
                        continue
                    #calcAttraction
                    attract = trafficCellDict[destination].attractivity[purposForJourney]
                    #calc excpected resistance and delta resistance
                    if step == 0 :
                        expextedResistanceGroup[popGroupKey] = resistance
                        deltaResistanceGroup[popGroupKey] = 0
                    else:
                        deltaResistanceGroup[popGroupKey] = resistance - trafficCell.expectedResistance[purposForJourney][destination][mode][popGroupKey]
                        expextedResistanceGroup[popGroupKey] = weightSmoothing * resistance + (1-weightSmoothing)*trafficCell.expectedResistance[purposForJourney][destination][mode][popGroupKey]

                    tempRatio = float(attract)/float(resistance)
                    sumRatio[popGroupKey] += tempRatio
                    groupRatio[popGroupKey] = tempRatio
                modeRatio[mode] = groupRatio
                expextedResistanceModeGroup[mode] = expextedResistanceGroup
                deltaResistanceModeGroup[mode] = deltaResistanceGroup
            ratioAttractivityResistance[destination] = modeRatio
            expextedResistanceDesModeGroup[destination] = expextedResistanceModeGroup
            deltaResistanceDesModeGroup[destination] = deltaResistanceModeGroup

        # calcGroupPart for purpose, destination and mode
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
                    if ratio == 0:
                        continue
                    if step == 0:
                        groupPartDemand[group] = (ratio/sumRatio[group])*trafficDemandPerGroup[group]
                        if ratio > sumRatio[group]:
                            print('!!! ratio > sumRatio[popGroupKey] ')
                    else:
                        evaluatorGroup = groupDict[group].calcEvaluatorGroup(deltaResistanceDesModeGroup[destination][mode][group])
                        groupPartDemand[group] = (ratio/sumRatio[group])*trafficDemandPerGroup[group]*evaluatorGroup + (1-evaluatorGroup) * trafficCell.purposeSestinationModeGroup[purposForJourney][destination][mode][group]
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
        trafficCell.expectedResistance[purposForJourney] = expextedResistanceDesModeGroup
        


def updateConnectionParamsAll(trafficCellDict):
    for trafficCell in trafficCellDict.values():
        trafficCell.updateConnectionParams()


def updateInhabitantsAll(trafficCellDict, year):
    for trafficCell in trafficCellDict.values():
        trafficCell.updateInhabitants(year)

######################
#
# Simulation one step
#
######################


def calcSimulationStep(trafficCellDict, groupDict, step, stepsPerYear, startYear, jsonParameter):

    choseDestinationAndMode(trafficCellDict, groupDict, 'work', step, jsonParameter)
    updateConnectionParamsAll(trafficCellDict)

    #update inhabitants every year
    if step % stepsPerYear == 0 and step != 0:
        year = startYear + step/stepsPerYear
        updateInhabitantsAll(trafficCellDict, year)



######################
#
# Simulation all steps
#
######################


def runSimulation(trafficCellDict, groupDict, jsonSimConfig, jsonParameter):
    stepsPerYear = jsonSimConfig["steps_per_year"]
    startYear=jsonSimConfig["start_year"]
    years = jsonSimConfig['simulation_years']
    steps = years*stepsPerYear

    listOfFiles = []
    

    # {timestep:{startCell:{Purpose{destination: { mode:{popGroup: trips}}}}
    resultOfSimulation = defaultdict()

    for st in range(0, steps):
        # MAIN Calculation
        calcSimulationStep(trafficCellDict, groupDict, st, stepsPerYear, startYear, jsonParameter)
        # write values
        startCellDict = defaultdict()
        for cellKey, cell in trafficCellDict.items():
            startCellDict[cellKey] = dict([('Sum_Trips_per_Mode', cell.purposeDestinationMode),
                                           ('Trips_per_group', cell.purposeSestinationModeGroup)])
            # startCellDict[cellKey]=cell.purposeSestinationModeGroup

        # Save results of simulation stepwise in JSON and get the list of Filenames
        listOfFiles.append(resultPerStepInFolders(startCellDict, jsonSimConfig["scenario_name"], jsonSimConfig["sim_ID"], st))
        # Save result of simulation in Dict
        resultOfSimulation[st] = startCellDict

        if st % stepsPerYear == 0:
            print("year: " + str(st/stepsPerYear))

    # Config for visualisation
    creatSimConfigFile(jsonSimConfig["sim_ID"], listOfFiles, steps, jsonSimConfig)

    return resultOfSimulation
