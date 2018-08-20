from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
from DataHandler import TrafficCellReaderCSV as TrafficCellReader
from DataHandler import inhabitantReaderCSV as inhabitantReader
from collections import defaultdict


#---List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.possibleAttributes,
    PopulationGroup.impossibleCombinations
    ) 

print(groupeList[0])

#---Generate TrafficCells
trafficCellDict=defaultdict()
trafficCellsInitDict = TrafficCellReader()
#print(trafficCellsInitDict)
for cellKey, cellName in trafficCellsInitDict.items():
    #set Name and GKZ of 
    trafficCellDict[cellKey]=TrafficCell(cellName,cellKey)

print(trafficCellDict[61059])

#---populate TrafficCell
inhabitantReader(trafficCellDict,"inhabitants")
print(trafficCellDict[61059].inhabitants)

for TC in trafficCellDict.values():
    PopulationGroup.calculatePopulation(TC)
#PopulationGroup.calculatePopulation(trafficCellDict[61059])
print(trafficCellDict[61059].populationParamsPerGroup)



