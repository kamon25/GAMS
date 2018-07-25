from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
import DataHandler
from collections import defaultdict


#---List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.possibleAttributes,
    PopulationGroup.impossibleCombinations
    ) 

print(groupeList[0])

#---Generate TrafficCells
trafficCellDict=defaultdict()
trafficCellsInitDict = DataHandler.TrafficCellReaderCSV()
#print(trafficCellsInitDict)
for cellKey, cellName in trafficCellsInitDict.items():
    #set Name and GKZ of 
    trafficCellDict[cellKey]=TrafficCell(cellName,cellKey)

print(trafficCellDict[60101])

#---populate TrafficCell
DataHandler.inhabitantReaderCSV(trafficCellDict,"inhabitants")
print(trafficCellDict[60101].inhabitants)



