import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import loadSimConfig
from DataHandler import loadParameterConfig
from DataHandler import cellListToJson
from DataHandler import groupDictToJson
from DataHandler import graphToJson
from DataHandler import connectionsToJson
from DataHandler import destinationsModesToJson
from DataHandler import resultOfSimulationToJson
from DataHandler import saveTrafficCells as saveTC
from DataHandler import loadTrafficCellDict as loadTC
from DataHandler import createOutputDirectory
from DataHandler import createScenarioConfigFile

from Infrastructure import ConInfrastructure as ConInfra

from TrafficEvaluation import generatePopulationGroups as generatePopulationGroups
from TrafficEvaluation import generateTrafficCells as generateTrafficCells
from TrafficEvaluation import calcAllPathsForTrafficCell
from TrafficEvaluation import choseDestinationAndMode
from TrafficEvaluation import runSimulation

from visualGAMS import plotConnectionComparison
from visualGAMS import plotModalSplitConnections
from visualGAMS import plotModalSplitOverAllCells
from visualGAMS import plotModalSplitwithinCells

# --- load Config-File
jsonSimConfig = loadSimConfig()
jsonParameter = loadParameterConfig()
# --- create output folder
createOutputDirectory(jsonSimConfig["scenario_name"])

# --- global Values and Assumptions
trafficPeakPercentage=jsonParameter["trafficPeakPercentage"]


# ---List of populationgroups in the area
groupDict = generatePopulationGroups(jsonParameter)
print(groupDict.keys())

groupDictToJson(groupDict, jsonSimConfig["scenario_name"])


#############################
# ---Generate TrafficCells
trafficCellDict = generateTrafficCells(jsonParameter)
print("TrafficCells generated")
saveTC(trafficCellDict)


# -----reload TrafficCells
# trafficCellDict=loadTC()
# print(trafficCellDict['61059'].inhabitants)
#######################################

cellListToJson(trafficCellDict, jsonSimConfig["scenario_name"])

#---- print Employed:
for tc in trafficCellDict.values():
    tc.printEmployed(groupDict)

# --- shortest Path:
ConInfra.bildGraph()

print(ConInfra.getShortestPaths_withStartMode(
    '60611', '60101', trafficCellDict, jsonParameter))

# Remove comment if changes in TrafficCell!!!
calcAllPathsForTrafficCell(trafficCellDict)

for connection in trafficCellDict['61059'].pathConnectionList['60101']['car']:
    print("here connection distance: " + str(connection.distance))

# ---saveTC
# saveTC(trafficCellDict)


# for path in trafficCellDict[61059].shortestPaths[60101].values():
#     print(path)
#     print(len(path))


# Start of destination choice
publicTransportCost = jsonSimConfig["publittransport_Cost"]
for tC in trafficCellDict.values():
    tC.calcConnectionParams(jsonSimConfig["carCostPer_KM"], publicTransportCost, jsonParameter)

# Run Simulation
resultDict = runSimulation(trafficCellDict, groupDict, jsonSimConfig, jsonParameter)
# Write Connections
connectionsToJson(trafficCellDict,jsonSimConfig["scenario_name"], 30)
createScenarioConfigFile(jsonSimConfig)


#############

plotConnectionComparison(trafficCellDict['60608'].pathConnectionList['60624']['car'][0],trafficCellDict['60608'].pathConnectionList['60624']['publicTransport'][0])
plotModalSplitConnections(trafficCellDict)
plotModalSplitOverAllCells(trafficCellDict)
plotModalSplitwithinCells(trafficCellDict)


###########

print(trafficCellDict['60101'].expectedResistance['work']['61059']['car']['popGroup2'])

#########

