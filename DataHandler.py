import csv
import math
import numpy as np
import pandas as pd
from collections import defaultdict
import simplejson as json
from networkx.readwrite import json_graph
import pickle
import os
import datetime

# Filepath config
pathConfigSim = 'config_sim.json'
pathConfigParameter = 'config_parameter.json'

# Filepaths Data
pathTrafficCellsCSV = './Data/Gemeinde_Liste_V1.csv'
pathPopulationAgeGroupsCSV = 'Data/STMK_01012017_AGE.csv'
pathPopulationSexCSV = 'Data/STMK_01012017_SEX.csv'
pathPopulationEmployment = 'Data/OGDEXT_AEST_GEMTAB_1.csv'
pathPopulationCarDensity = 'Data/carDensity.csv'
pathPopulationMobile= 'Data/mobilePersons.csv'
pathPopulationCarAvailable = 'Data/carAvailability.csv'
pathPopulationForecast = 'Data/STMK_2015_2030_PROJ.csv'

# Filepaths traffic network
pathAutobahnNeighbour = 'Data/Nachbarschaftsliste_Autobahn.csv'
pathCountryRoadNeighbour = 'Data/Nachbarschaftsliste_Standard.csv'
pathTrainNeighbour = 'Data/Nachbarschaftsliste_Zug.csv'
pathConnectionWeights = 'Data/weightConnections.csv'
pathDefaultCapacity = 'Data/defaultCapacity.csv'
pathBasicLoad = 'Data/basicLoad.csv'


# Filepaths Output
standardOutpath = 'JsonOutput/scenarios'
# spezific Files
pathTrafficCellData = 'trafficCellData.json'
pathPopGroups = 'popGroups.json'
pathNetworkgraph = 'networkgraph.json'
pathConnections = 'connections.json'
pathDestinationsOfGroupsInCells = 'destinationsModesOfGroups.json'
pathSimResult = 'simResult.json'
pathSimResultPerStep = 'simResultsPerStep/simResult-step'
pathSimFolder ='simulations'
pathSimResultPerStepinFolder = pathSimFolder + '/simResul'
pathResulFolder = 'simResul'
pathSimConfigOutput = 'simulation_config.json'
pathScenarioConfigOutput = 'scenario_config.json'

# Filepaths storage
pathTrafficCellStorage = 'Storage/trafficCellObjects'

########################################
#
#     INPUT methods
#
#########################################


def loadSimConfig():
    with open(pathConfigSim) as f:
        jsonConfig = json.load(f)
    return jsonConfig


def loadParameterConfig():
    with open(pathConfigParameter) as f:
        jsonParameter = json.load(f)
    return jsonParameter


def TrafficCellReaderCSV():
    TarfficCells = defaultdict()
    with open(pathTrafficCellsCSV) as f:
        reader = csv.reader(f, delimiter=';')
        skip = True
        for row in reader:
            if(skip):
                skip = False
                continue

            TarfficCells[row[0]] = row[1]

    return TarfficCells


def attractionReaderCSV(cellID, tripPrupose):
    if tripPrupose is "work":
        df = pd.read_csv('Data/OGDEXT_AEST_GEMTAB_1.csv', sep=';',
                         na_values=['NA'], thousands=".", dtype={'GCD': str})
        df2 = df[df["JAHR"] == df["JAHR"].max()]
        dfBetrachtung = df2.set_index('GCD')
        workplaceCorresponding = {"work": "BESCH_AST"}

        attractionWork = float(
            dfBetrachtung.loc[cellID][workplaceCorresponding[tripPrupose]])
        return attractionWork


def inhabitantReaderCSV(trafficCellDict, *paramsToRead):
    dfGemList = pd.read_csv(pathTrafficCellsCSV, encoding="ISO-8859-1",
                            sep=';',  na_values=['NA'], dtype={"GKZ": str})

    if("inhabitants" in paramsToRead):
        df = pd.read_csv(pathPopulationAgeGroupsCSV, encoding="ISO-8859-1",
                         sep=';',  na_values=['NA'], dtype={'LAU_CODE': str})
        # print(df.head())
        # print(dfGemList.head())
        dfBetrachtung = df[df["LAU_CODE"].isin(dfGemList["GKZ"])]

        pop_total = dfBetrachtung.set_index('LAU_CODE')["POP_TOTAL"]
        # print(pop_total.to_dict().keys())

        for cellID, cell in trafficCellDict.items():
            # Convertation to int maybe needed
            cell.inhabitants = pop_total.to_dict()[cellID]
            cell.inhabitantForecast = inhabitantForecastReader(cellID)


def inhabitantForecastReader(cellID):
    df = pd.read_csv(pathPopulationForecast, encoding="ISO-8859-1",
                     sep=';',  na_values=['NA'], dtype={'LAU_CODE': str})
    dfBetrachtung = df.set_index('LAU_CODE')

    popYear = defaultdict()
    for dataColumNames in list(dfBetrachtung):
        headSplit = dataColumNames.split("_")
        if headSplit[0] == "POP":
            popYear[int(headSplit[1])
                    ] = dfBetrachtung.loc[cellID][dataColumNames]

    return popYear


def AttributeReaderCSV(cellID, popGroup, paramToRead):

    # ---read agegroups
    if paramToRead is "agegroup":
        df = pd.read_csv(pathPopulationAgeGroupsCSV, encoding="ISO-8859-1",
                         sep=';',  na_values=['NA'], dtype={'LAU_CODE': str})
        dfBetrachtung = df.set_index('LAU_CODE')
        agegroupCount = defaultdict(int)

        for agegroupe in popGroup.possibleAttributes[paramToRead]:
            print(agegroupe)
            agegroupeSum = 0

            for dataColumNames in list(dfBetrachtung):
                headSplit = dataColumNames.split("_")

                if headSplit[0] == "POP" and headSplit[1].isdigit():
                    # group in data is completlely in the defined group
                    if int(headSplit[1]) >= agegroupe[0] and ((int(headSplit[2]) <= agegroupe[1]) if len(headSplit) > 2 else int(headSplit[1]) <= agegroupe[1]):
                        agegroupeSum = agegroupeSum + \
                            dfBetrachtung.loc[cellID][dataColumNames]

                    # group in data is a part of the defined group
                    elif int(headSplit[1]) >= agegroupe[0] and int(headSplit[1]) < agegroupe[1]:
                        upperBound = int(headSplit[2]) if len(
                            headSplit) > 2 else agegroupe[1]
                        grouppart = dfBetrachtung.loc[cellID][dataColumNames]/(
                            upperBound-int(headSplit[1]))*(agegroupe[1]-int(headSplit[1]))
                        agegroupeSum = agegroupeSum + grouppart
                    elif int(headSplit[1]) < agegroupe[0] and ((int(headSplit[2]) > agegroupe[0]) if len(headSplit) > 2 else True):
                        upperBound = int(headSplit[2]) if len(
                            headSplit) > 2 else agegroupe[1]
                        grouppart = dfBetrachtung.loc[cellID][dataColumNames]/(
                            upperBound-int(headSplit[1]))*(upperBound-agegroupe[0])
                        agegroupeSum = agegroupeSum + grouppart

                    # defined group is completely in
                    elif int(headSplit[1]) <= agegroupe[0] and ((int(headSplit[2]) >= agegroupe[1]) if len(headSplit) > 2 else True):
                        if len(headSplit) > 2:
                            rangeData = int(headSplit[2]-headSplit[1])
                            rangeDefinetGroup = agegroupe[1]-agegroupe[0]
                            grouppart = dfBetrachtung.loc[cellID][dataColumNames] * \
                                rangeDefinetGroup/rangeData
                        else:
                            rangeData = int(
                                popGroup.possibleAttributes[paramToRead][-1][1]-headSplit[1])
                            rangeDefinetGroup = agegroupe[1]-agegroupe[0]
                            grouppart = dfBetrachtung.loc[cellID][dataColumNames] * \
                                rangeDefinetGroup/rangeData

            agegroupCount[agegroupe] = agegroupeSum
        # print(agegroupCount)
        return agegroupCount

    # ---read gender
    if paramToRead is "gender":
        df = pd.read_csv(pathPopulationSexCSV, encoding="ISO-8859-1",
                         sep=';',  na_values=['NA'], dtype={'LAU_CODE': str})
        dfBetrachtung = df.set_index('LAU_CODE')
        genderCount = defaultdict(int)
        genderCorresponding = {"male": "MEN", "female": "WOMEN"}

        for gender in popGroup.possibleAttributes[paramToRead]:
            print(gender)

            for dataColumNames in list(dfBetrachtung):
                headSplit = dataColumNames.split("_")

                if headSplit[0] == "POP" and headSplit[1] == genderCorresponding[gender]:
                    genderCount[gender] = dfBetrachtung.loc[cellID][dataColumNames]

        return genderCount

    # ---read employment rate
    if paramToRead is "employment":
        df = pd.read_csv('Data/OGDEXT_AEST_GEMTAB_1.csv', sep=';',
                         na_values=['NA'], decimal=',', dtype={'GCD': str})
        df2 = df[df["JAHR"] == df["JAHR"].max()]
        dfBetrachtung = df2.set_index('GCD')
        employmentCorresponding = {"employment": "EWTQ_15BIS64"}

        employmentRate = {"employmentRate_15_64": float(
            dfBetrachtung.loc[cellID][employmentCorresponding[paramToRead]])}
        return employmentRate

    # ---read car density
    if paramToRead is 'carAvailable':
        df = pd.read_csv(pathPopulationCarAvailable, sep=';', na_values=[
                         'NA'], decimal='.', dtype={'GKZ': str})
        dfBetrachtung = df.set_index('GKZ')

        agegroupRate = defaultdict(float)

        for agegroup in popGroup.possibleAttributes['agegroup']:
            agegroupeSum = 0
            count = 0

            for dataColumNames in list(dfBetrachtung):
                headSplit = dataColumNames.split("_")

                if headSplit[0] == "POP" and headSplit[1].isdigit():

                    if int(headSplit[1]) >= agegroup[0] and int(headSplit[1]) <= agegroup[1]:
                        agegroupeSum += dfBetrachtung.loc[cellID][dataColumNames]
                        count += 1

                    if len(headSplit) < 3:
                        continue
                    elif int(headSplit[2]) >= agegroup[0] and int(headSplit[2]) <= agegroup[1]:
                        agegroupeSum += dfBetrachtung.loc[cellID][dataColumNames]
                        count += 1

            if count == 0:
                rate = 0.0
            else:
                rate = float(agegroupeSum)/float(count)
            agegroupRate[agegroup] = rate
        return agegroupRate

        # code to read the density
        # df = pd.read_csv(pathPopulationCar, sep=';',
        #                  na_values=['NA'], decimal='.', dtype={'GKZ': str})
        # dfBetrachtung = df.set_index('GKZ')
        # carCorresponding = {"carAviable": "PKW-Dichte"}

        # carDensity =  float(dfBetrachtung.loc[cellID][carCorresponding[paramToRead]])
        # return carDensity


# ---read human behavior in traffic
def behaviorReaderDummy(paramToRead, cellID , possibleAttributes):
    # --- read travel time budget
    if (paramToRead == "travelTimeBudget"):
        ttbSchweizerMikriozenzus = {(6, 24): (88.61, 90.19, 91.77), (25, 64): (
            94.91, 96.02, 97.13), (65, 100): (72.89, 74.81, 76.64)}
        ttbAgegroups = defaultdict()

        # -- chose data with smallest difference
        for agegroup in possibleAttributes["agegroup"]:
            keyForSmalestDifference = None
            smallestDifference = None
            for key in ttbSchweizerMikriozenzus.keys():
                diff = math.pow(agegroup[0]-key[0], 2) + \
                    math.pow(agegroup[1]-key[1], 2)
                if keyForSmalestDifference == None:
                    keyForSmalestDifference = key
                    smallestDifference = diff
                elif smallestDifference > diff:
                    keyForSmalestDifference = key
                    smallestDifference = diff
            ttbAgegroups[agegroup] = ttbSchweizerMikriozenzus[keyForSmalestDifference]

        return ttbAgegroups

    # --- read travel time budget
    if (paramToRead == "tripRate"):
        waysSchweizerMikriozenzus = {(6, 24): (3.85, 3.89, 3.93), (25, 64): (
            3.87, 3.9, 3.93), (65, 100): (2.69, 2.73, 2.76)}
        tripsAgegroups = defaultdict()

        # -- chose data with smallest difference
        for agegroup in possibleAttributes["agegroup"]:
            keyForSmalestDifference = None
            smallestDifference = None
            for key in waysSchweizerMikriozenzus.keys():
                diff = math.pow(agegroup[0]-key[0], 2) + \
                    math.pow(agegroup[1]-key[1], 2)
                if keyForSmalestDifference == None:
                    keyForSmalestDifference = key
                    smallestDifference = diff
                elif smallestDifference > diff:
                    keyForSmalestDifference = key
                    smallestDifference = diff
            tripsAgegroups[agegroup] = waysSchweizerMikriozenzus[keyForSmalestDifference]

        return tripsAgegroups


    if (paramToRead == "mobility"):
        mobilityCarAviable = defaultdict()

        df = pd.read_csv(pathPopulationMobile, sep=';', na_values=['NA'], decimal='.', dtype={'GKZ': str})
        dfBetrachtung = df.set_index('GKZ')

        for carAviable in possibleAttributes['carAvailable']:
            if carAviable == 'available':
                mobilityCarAviable[carAviable] = float(dfBetrachtung.loc[cellID]['Mobil_Fuehrerschein'])
            elif carAviable == 'notAvailable':
                mobilityCarAviable[carAviable] = float(dfBetrachtung.loc[cellID]['Mobil_ohneFuehrerschein'])
            else:
                print('Fehler in der Bezeichung der Autoverfügbarkeit')
                mobilityCarAviable[carAviable] = 0.85
        
        return mobilityCarAviable



# Information about connection between the trafficCells


def readConnectionRows(connectionToRead):
    data = []
    filename = "None"

    if connectionToRead == "countryroad":
        filename = pathCountryRoadNeighbour
    elif connectionToRead == "train":
        filename = pathTrainNeighbour
    elif connectionToRead == "autobahn":
        filename = pathAutobahnNeighbour
    else:
        raise ValueError

    with open(filename) as f:
        reader = csv.reader(f, delimiter=';')
        skip = True
        for row in reader:
            if(skip):
                skip = False
                continue

            data.append(";".join(row))

    return data

# read weight connection


def redConnectionWeights():
    variables = defaultdict(float)
    with open(pathConnectionWeights) as f:
        reader = csv.reader(f, delimiter=';')
        skip = True
        for row in reader:
            if(skip):
                skip = False
                continue

            variables[row[0]] = float(row[1])

    return variables


# read default capacity for connectiontypes (estimation)
def readDefaultCapacity():
    capacity = defaultdict(float)
    with open(pathDefaultCapacity) as f:
        reader = csv.reader(f, delimiter=';')
        skip = True
        for row in reader:
            if(skip):
                skip = False
                continue

            capacity[row[0]] = float(row[1])

    return capacity


def readBasicLoad():
    basicLoad = defaultdict(float)
    with open(pathBasicLoad) as f:
        reader = csv.reader(f, delimiter=';')
        skip = True
        for row in reader:
            if(skip):
                skip = False
                continue

            basicLoad[row[0]] = float(row[1])

    return basicLoad

#################################
#
#   OUTPUT methods
#
#################################


def createOutputDirectory(scenarioName):
    folderPath = '/'.join([standardOutpath,
                           '-'.join(['scenario', scenarioName])])

    if not os.path.exists(folderPath):
        os.makedirs(folderPath)


##########
# JSON Encoder
##########


def cellListToJson(trafficCellDict, scenarioName):
    outpath = '/'.join([standardOutpath, '-'.join(['scenario',
                                                   scenarioName]), pathTrafficCellData])
    print(outpath)
    outDict = defaultdict()

    for key, cell in trafficCellDict.items():
        if cell.popPerGroup != None:
            outDict[key] = cell.toDictWithPopGroup()
        else:
            outDict[key] = cell.toDict()

    with open(outpath, 'w') as fp:
        json.dump(outDict, fp, separators=(',', ':'), indent=4)
    print("Output updated: TrafficCells")


def groupDictToJson(groupDict, scenarioName):
    outpath = '/'.join([standardOutpath,
                        '-'.join(['scenario', scenarioName]), pathPopGroups])

    outDict = defaultdict()

    for key, group in groupDict.items():
        outDict[key] = group._attributes

    with open(outpath, 'w') as fp:
        json.dump(outDict, fp, separators=(',', ':'), indent=4)
    print("Output updated: Groups")


def graphToJson(networkGraph):
    d = json_graph.node_link_data(networkGraph)
    with open(pathNetworkgraph, 'w') as fp:
        json.dump(d, fp, indent=4)
    print('Wrote node-link as JSON to' + pathNetworkgraph)


def connectionsToJson(trafficCellDict, scenarioName, step):
    connections = set()
    mostOccupied = list()
    lessOccupied = list()
    outputList = []
    outpath = '/'.join([standardOutpath,
                        '-'.join(['scenario', scenarioName]), pathConnections])

    for trafficCell in trafficCellDict.values():
        for cellValues in trafficCell.pathConnectionList.values():
            for modeValues in cellValues.values():
                connections = connections.union(set(modeValues))

    for tempConnection in connections:
        outputList.append(tempConnection.toDict(step))
        if tempConnection.occupancy[step] >= 1.0:
            mostOccupied.append(tempConnection.toDict(step))
        elif tempConnection.occupancy[step] < 0.1:
            lessOccupied.append(tempConnection.toDict(step))



    #d={'links': outputSet}

    with open(outpath, 'w') as fp:
        json.dump(outputList, fp, indent=4)
    print('Wrote connections as JSON  to' + outpath)

    with open('internChecks/mostOccupied.json', 'w') as fp:
        json.dump(mostOccupied, fp, indent=4)
        
    with open('internChecks/lessOccupied.json', 'w') as fp:
        json.dump(lessOccupied, fp, indent=4)


def destinationsModesToJson(trafficCellDict, scenarioName):
    outDict = defaultdict()
    outpath = '/'.join([standardOutpath, '-'.join(['scenario',
                                                   scenarioName]), pathDestinationsOfGroupsInCells])

    for tc in trafficCellDict.values():
        tempPurposeDict = defaultdict()
        for purp, desDict in tc.purposeSestinationModeGroup.items():
            tempDesDict = defaultdict()
            for des, modeDict in desDict.items():
                tempModeDict = defaultdict()
                for mode, popDict in modeDict.items():
                    tempPopDict = defaultdict()
                    for popGr, trip in popDict.items():
                        tempPopDict[popGr] = trip
                    tempModeDict[mode] = tempPopDict
                tempDesDict[des] = tempModeDict
            tempPurposeDict[purp] = tempDesDict
        outDict[tc] = tempPurposeDict

    with open(outpath, 'w') as fp:
        json.dump(outDict, fp, indent=4)
    print('Wrote node-link JSON data to' + pathDestinationsOfGroupsInCells)


def resultOfSimulationToJson(resultDict, scenarioName):
    # {timestep:{startCell.ID:{Purpose{destination_ID: { mode:{popGroup: trips}}}}
    outDict = resultDict
    outpath = '/'.join([standardOutpath,
                        '-'.join(['scenario', scenarioName]), pathSimResult])
    with open(outpath, 'w') as fp:
        json.dump(outDict, fp, indent=4)
    print('Wrote result JSON data to' + pathSimResult)


def resultSimStepsToJson(stepResultDic, scenarioName, step):
    # {startCell.ID:{Purpose{destination_ID: { mode:{popGroup: trips}}}}
    outDict = stepResultDic
    outpath = pathSimResultPerStep + '-' + str(step) + '.json'
    outpath = '/'.join([standardOutpath,
                        '-'.join(['scenario', scenarioName]), outpath])

    with open(outpath, 'w') as fp:
        json.dump(outDict, fp, indent=4)
        print('Wrote step result JSON data to' + outpath)


def resultPerStepInFolders(stepResultDic, scenarioName, simID, step):
    path = '/'.join([standardOutpath, '-'.join(['scenario',
                                                scenarioName]), '-'.join([pathSimResultPerStepinFolder,simID])])

    for keys, outDict in stepResultDic.items():
        # createFolders
        folderPath = path + '/' + keys
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        # writeFiles
        filename = 'simResult' + '-' + str(step) + '.json'
        outpath = folderPath + '/' + filename

        with open(outpath, 'w') as fp:
            json.dump(outDict, fp, indent=4)
            print('Wrote step result JSON data to' + outpath)

    return filename


def creatSimConfigFile(simID, listOfFiles, steps, jsonSimConfig, jsonParameter):
    outpath = '/'.join([standardOutpath, '-'.join(['scenario', jsonSimConfig["scenario_name"]]),
                        '-'.join([pathSimResultPerStepinFolder,jsonSimConfig['sim_ID']]), pathSimConfigOutput])
    startTimeObject = datetime.date(jsonSimConfig['start_year'], 1, 1)
    endTimeObject = startTimeObject+datetime.timedelta(days=steps*365/12)

    #Simulation Config
    simulationID = ('simulationID', simID)
    simulationName = ('simulationName', jsonSimConfig['simulation_name'])
    simulationDescription = ('simulationDescription', jsonSimConfig['simulation_description'])
    startDate = ('startDate_YYYYMM', startTimeObject.strftime('%Y%m'))
    endDate = ('endDate_YYYYMM', endTimeObject.strftime('%Y%m'))
    simulationCalculationStepSize_days = (
        'simulationCalculationStepSize_months', int(12/jsonSimConfig["steps_per_year"]))
    simulationPresentationStepSize_days = (
        'simulationPresentationStepSize_months', int(12/jsonSimConfig["presentation_steps_per_year"]))

    outDict = dict([simulationID, simulationName, simulationDescription, startDate, endDate, simulationCalculationStepSize_days, simulationPresentationStepSize_days,
                    ('simulationResultStepFileNames', listOfFiles)])

    #Policy
    carCostPer_KM={"Name":"Autokosten", "Wert": jsonSimConfig["carCostPer_KM"], "Beschreibung": "Kosten in Euro pro Kilometer für Autofahrten"}
    publicTransportCost={"Name":"Kosten öffentlicher Verkehr", "Wert": jsonSimConfig["publittransport_Cost"], "Beschreibung": "Kosten für den öffentlichen Verkehr auf Basis der Tarifzonen"}

    defaultCapacity = readDefaultCapacity()

    capacity_car_autobahn = defaultCapacity['car_autobahn']
    capacity_car_countryroad = defaultCapacity['car_countryroad']
    capacity_publicTransport_train = defaultCapacity['publicTransport_train']
    capacity_publicTransport_bus = defaultCapacity['publicTransport_bus']
    capacity_bicycle_countryroad = defaultCapacity['bicycle_countryroad']

    capacity = {"Name": "Verbindungskapazitäten", "Wert": {"Autobahn": capacity_car_autobahn, "Landstraße": capacity_car_countryroad, "S-Bahn": capacity_publicTransport_train, "Bus": capacity_publicTransport_bus, "Fahrrad": capacity_bicycle_countryroad}, "Beschreibung": "Durschnittliche Kapazitäten der Verbindungen zwischen den Konten in Personen pro Stunde"}

    averageSpeed = redConnectionWeights()

    speed_car_autobahn = round(80.0 / averageSpeed['car_autobahn'],2)
    speed_car_countryroad =  round(80.0 / averageSpeed['car_countryroad'],2)
    speed_publicTransport_train =  round(80.0 / averageSpeed['publicTransport_train'],2)
    speed_publicTransport_bus =  round(80.0 / averageSpeed['publicTransport_bus'],2)
    speed_bicycle_countryroad =  round(80.0 / averageSpeed['bicycle_countryroad'],2)

    speed = {"Name": "Verbindungsgeschwindigkeiten", "Wert": {"Autobahn": speed_car_autobahn, "Landstraße": speed_car_countryroad, "S-Bahn": speed_publicTransport_train, "Bus": speed_publicTransport_bus, "Fahrrad": speed_bicycle_countryroad}, "Beschreibung": "Durschnittliche Geschwindigkeit der Verbindungen zwischen den Konten in Kilometer pro Stunde"}

    speedInZone = {"Name": "Zonengeschwindigkeiten", "Wert": {"Auto": jsonParameter["speedInZoneCar"], "ÖV": jsonParameter["speedInZonePT"], "Fahrrad": jsonParameter["speedInZoneBicycle"], "Fußgänger": jsonParameter["speedInZoneWalk"]}, "Beschreibung": "Durschschnittliche Geschwindigkeit die innerhalb von Verkehrsknoten auftretten in Kilometer pro Stunde"}

    policyDict = {"carCostPer_KM": carCostPer_KM, "publicTransportCost_KM": publicTransportCost, "capacity":capacity, "speed": speed, "speedInZone": speedInZone}

    
    #Add Policy to Outdict

    outDict['policy'] = policyDict


    with open(outpath, 'w', encoding='utf-8') as fp:
        json.dump(outDict, fp, indent=4, ensure_ascii=False)
        print('Wrote step result JSON data to' + outpath)


def createScenarioConfigFile(jsonSimConfig):
    outpath = '/'.join([standardOutpath, '-'.join(['scenario',
                                                   jsonSimConfig["scenario_name"]]), pathScenarioConfigOutput])
    
    checkPath = '/'.join([standardOutpath, '-'.join(['scenario',
                                                   jsonSimConfig["scenario_name"]]), pathSimFolder])
    
    print(checkPath)
    folderlist = os.listdir(checkPath) 
    print(folderlist)
    outDict = {'scenarioName':jsonSimConfig['scenario_name'], 'scenarioDescription': jsonSimConfig['scenario_description'], 'mapData': {"POLITICAL_AREA_SHAPE_FILE_URL": "GemeindenBMNM34_2015.zip"}, 'gamsData': {"POLITICAL_AREA_GAMS_DATA_URL": "trafficCellData.json", "BEHAVIOURAL_HOMOGENIOUS_GROUP_GAMS_DATA_URL": "popGroups.json",
                                                                                                                            "TRAFFIC_NETWORK_GRAPH_GAMS_DATA_URL": "connections.json", "AVAILABLE_TRAFFIC_STATE_SIMULATON_GAMS_DATA": {"baseFolder": "simulations", "simulationDataFolderNames": folderlist}}}

    with open(outpath, 'w', encoding='utf-8') as fp:
        json.dump(outDict, fp, indent=4, ensure_ascii=False)
        print('Wrote step result JSON data to' + outpath)


#################################
#
#   storing data methods
#
#################################

def saveTrafficCells(TrafficCellDict):
    with open(pathTrafficCellStorage, 'wb') as fp:
        pickle.dump(TrafficCellDict, fp)


def loadTrafficCellDict():
    with open(pathTrafficCellStorage, 'rb') as fp:
        trafficCellDict = pickle.load(fp)
    return trafficCellDict
