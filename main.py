from collections import defaultdict

from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import cellListToJson
from DataHandler import groupListToJson
from DataHandler import graphToJson
from DataHandler import saveTrafficCells as saveTC
from DataHandler import loadTrafficCellDict as loadTC
from Infrastructure import ConInfrastructure as ConInfra

from TrafficEvaluation import generatePopulationGroups as generatePopulationGroups
from TrafficEvaluation import generateTrafficCells as generateTrafficCells
from TrafficEvaluation import calcAllPathsForTrafficCell





#---List of populationgroups in the area
groupList = generatePopulationGroups()
print(groupList[0])

# groupListToJson(groupList)


#############################
#---Generate TrafficCells
# trafficCellDict=generateTrafficCells()
# saveTC(trafficCellDict)
# print("done!!!!!!!!!!")

#-----reload TrafficCells
trafficCellDict=loadTC()
print(trafficCellDict[61059].inhabitants)
#######################################

# cellListToJson(trafficCellDict)

#--- shortest Path:
ConInfra.bildGraph()
print(ConInfra.getShortestPaths_withStartMode(61059, 60101, trafficCellDict))


calcAllPathsForTrafficCell(trafficCellDict)
print(trafficCellDict[61059].shortestPaths[60101])


# graphToJson(ConInfra.infraNetworkGraph)






