from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import TrafficCellReaderCSV as TrafficCellReader
from DataHandler import inhabitantReaderCSV as inhabitantReader
from DataHandler import attractionReaderCSV as attractionReader
from DataHandler import cellListToJson
from Infrastructure import ConInfrastructure as ConInfra

from collections import defaultdict



#---List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.possibleAttributes,
    PopulationGroup.impossibleCombinations
    ) 

print(groupeList[0])

#---Generate TrafficCells
trafficCellDict=defaultdict()
trafficCellsInitDict = TrafficCellReader() #Read the traffic cells in viewing space
#print(trafficCellsInitDict)
for cellKey, cellName in trafficCellsInitDict.items():
    #set Name and GKZ of traffic cells an instance the object
    trafficCellDict[cellKey]=TrafficCell(cellName,cellKey)
    print(cellName)


print(len(trafficCellDict))

#--- shortest Path:
ConInfra.bildGraph()
print(ConInfra.getShortestPath(60101, 61059, trafficCellDict))



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

#cellListToJson(trafficCellDict)

for tc in trafficCellDict.values():
    PopulationGroup.calculatePopulation(tc)
#PopulationGroup.calculatePopulation(trafficCellDict[61059])
print(trafficCellDict[61059].populationParamsPerGroup)

#cellListToJson(trafficCellDict)



