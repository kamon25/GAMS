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

from collections import defaultdict



#---List of populationgroups in the area
groupList = generatePopulationGroups()
print(groupList[0])

groupListToJson(groupList)


#############################
#---Generate TrafficCells
# trafficCellDict=generateTrafficCells()
# saveTC(trafficCellDict)
# print("done!!!!!!!!!!")

#-----reload TrafficCells
trafficCellDict=loadTC()
print(trafficCellDict[61059].inhabitants)

cellListToJson(trafficCellDict)

#--- shortest Path:
ConInfra.bildGraph()
print(ConInfra.getShortestPath(60101, 61059, trafficCellDict))

graphToJson(ConInfra.infraNetworkGraph)






