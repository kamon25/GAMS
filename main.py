import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import cellListToJson
from DataHandler import groupDictToJson
from DataHandler import graphToJson
from DataHandler import connectionsToJson
from DataHandler import destinationsModesToJson
from DataHandler import resultOfSimulationToJson
from DataHandler import saveTrafficCells as saveTC
from DataHandler import loadTrafficCellDict as loadTC
from Infrastructure import ConInfrastructure as ConInfra

from TrafficEvaluation import generatePopulationGroups as generatePopulationGroups
from TrafficEvaluation import generateTrafficCells as generateTrafficCells
from TrafficEvaluation import calcAllPathsForTrafficCell
from TrafficEvaluation import choseDestinationAndMode
from TrafficEvaluation import runSimulation

# --- global Values and Assumptions
trafficPeakPercentage=0.15


# ---List of populationgroups in the area
groupDict = generatePopulationGroups()
print(groupDict.keys())

groupDictToJson(groupDict)


#############################
# ---Generate TrafficCells
trafficCellDict = generateTrafficCells()
print("TrafficCells generated")
saveTC(trafficCellDict)


# -----reload TrafficCells
# trafficCellDict=loadTC()
# print(trafficCellDict['61059'].inhabitants)
#######################################

cellListToJson(trafficCellDict)

# --- shortest Path:
ConInfra.bildGraph()

print(ConInfra.getShortestPaths_withStartMode(
    '60611', '60101', trafficCellDict))

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
publicTransportCost = [2.4, 2.1, 2.1, 2, 2, 2,
                       2, 2, 2, 1.7, 1.6, 1.5, 1.5, 1.5, 1.5, 1.5]
for tC in trafficCellDict.values():
    tC.calcConnectionParams(0.42, publicTransportCost)

# Run Simulation
resultDict = runSimulation(trafficCellDict, groupDict, 3, 2018)
# Write Connections
connectionsToJson(trafficCellDict, 30)



#############
plt.figure(1)
plt.plot(trafficCellDict['60608'].pathConnectionList['60624']['car'][0].occupancy, label=trafficCellDict['60608'].pathConnectionList['60624']['car'][0].getConnectionType())
plt.plot(trafficCellDict['60608'].pathConnectionList['60624']['publicTransport'][0].occupancy, label=trafficCellDict['60608'].pathConnectionList['60624']['publicTransport'][0].getConnectionType())
plt.ylabel('Auslastung')
plt.legend()
plt.savefig('Pic/occupy.png')

plt.figure(2)
plt.plot(trafficCellDict['60608'].pathConnectionList['60624']['car'][0].stepLoad, label=trafficCellDict['60608'].pathConnectionList['60624']['car'][0].getConnectionType())
plt.plot(trafficCellDict['60608'].pathConnectionList['60624']['publicTransport'][0].stepLoad, label=trafficCellDict['60608'].pathConnectionList['60624']['publicTransport'][0].getConnectionType())
plt.ylabel('trips')
plt.legend()
plt.savefig('Pic/trips.png')

plt.figure(3)
plt.plot()
###########

print(trafficCellDict['60101'].expectedResistance['work']['61059']['car']['popGroup2'])