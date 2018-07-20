from Population.PopulationGroup import PopulationGroup
from Infrastructure.TrafficCell import TrafficCell
import DataHandler
from collections import defaultdict


#List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.possibleAttributes,
    PopulationGroup.impossibleCombinations
    ) 

#print(groupeList[0])

#Generate TrafficCells
trafficcelldict=defaultdict()
trafficCellsInitDict = DataHandler.TrafficCellReaderCSV()
print(trafficCellsInitDict)
for key, value in trafficCellsInitDict.items():
    trafficcelldict[key]=TrafficCell(value,key)

print(trafficcelldict["60101"])



