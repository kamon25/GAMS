from Population.PopulationGroup import PopulationGroup


#List of populationgroups in the area
groupeList = PopulationGroup.generateGroups(
    PopulationGroup.impossibleCombinations, 
    PopulationGroup.groupAttributesNames,
    PopulationGroup.possibleGender,
    PopulationGroup.possibleAgegroups,
    PopulationGroup.possibleEmploymentState) 

print(groupeList[0])


