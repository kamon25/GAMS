from Population.PopulationGroup import PopulationGroup


#List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.possibleAttributes,
    PopulationGroup.impossibleCombinations 
   ) 

print(groupeList[0])


