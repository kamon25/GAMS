from collections import defaultdict

from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import cellListToJson
from DataHandler import groupListToJson
from DataHandler import graphToJson
from DataHandler import destinationsModesToJson
from DataHandler import saveTrafficCells as saveTC
from DataHandler import loadTrafficCellDict as loadTC
from Infrastructure import ConInfrastructure as ConInfra

from TrafficEvaluation import generatePopulationGroups as generatePopulationGroups
from TrafficEvaluation import generateTrafficCells as generateTrafficCells
from TrafficEvaluation import calcAllPathsForTrafficCell
from TrafficEvaluation import choseDestinationAndMode





#---List of populationgroups in the area
groupList = generatePopulationGroups()
print(groupList[0])

# groupListToJson(groupList)


#############################
#---Generate TrafficCells
# trafficCellDict=generateTrafficCells()
# print("TrafficCells generated")
# saveTC(trafficCellDict)


#-----reload TrafficCells
trafficCellDict=loadTC()
print(trafficCellDict[61059].inhabitants)
#######################################

# cellListToJson(trafficCellDict)

#--- shortest Path:
ConInfra.bildGraph()

print(ConInfra.getShortestPaths_withStartMode(60611, 60101, trafficCellDict))

# Remove comment if changes in TrafficCell!!!
calcAllPathsForTrafficCell(trafficCellDict)
print(trafficCellDict[61059].shortestPaths[60101])

#---saveTC
#saveTC(trafficCellDict)




# for path in trafficCellDict[61059].shortestPaths[60101].values():
#     print(path)
#     print(len(path))


#graphToJson(ConInfra.infraNetworkGraph)


##### Start of destination choice
publicTransportCost=[2.4,2.1,2.1,2,2,2,2,2,2,1.7,1.6,1.5,1.5,1.5,1.5,1.5]
for tC in trafficCellDict.values():
    tC.calcConnectionParams(0.42, publicTransportCost)


choseDestinationAndMode(trafficCellDict, 'work')

destinationsModesToJson(trafficCellDict)

