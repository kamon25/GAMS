import csv
import math
import numpy as np 
import pandas as pd 
from collections import defaultdict

#Filepaths
pathTrafficCellsCSV = './Data/Gemeinde_Liste_V1.csv'
pathPopulationAgeGroupsCSV='Data/STMK_01012017_AGE.csv'
pathPopulationSexCSV='Data/STMK_01012017_SEX.csv'
pathPopulationEmployment='Data/OGDEXT_AEST_GEMTAB_1.csv'

def TrafficCellReaderCSV():
    TarfficCells = defaultdict()
    with open(pathTrafficCellsCSV) as f:
      reader = csv.reader(f, delimiter=';')
      skip = True
      for row in reader:
        if(skip):
          skip = False
          continue      
        
        TarfficCells[int(row[0])] = row[1]
    
    return TarfficCells

def inhabitantReaderCSV(trafficCellDict, *paramsToRead):
    dfGemList=pd.read_csv(pathTrafficCellsCSV,encoding = "ISO-8859-1",  sep=';',  na_values=['NA'])

    # reading Agegroups is currently not in use. Ageroups are set de AttributeReaderCSV
    if ("agegroupe" in paramsToRead):
      df=pd.read_csv(pathPopulationAgeGroupsCSV, encoding = "ISO-8859-1", sep=';',  na_values=['NA'])
      dfBetrachtung=df[df["LAU_CODE"].isin(dfGemList["GKZ"])]

      pop_0_14=dfBetrachtung.set_index('LAU_CODE')["POP_0_14"]
      pop_15_59=dfBetrachtung.set_index('LAU_CODE')["POP_15_29"] + dfBetrachtung.set_index('LAU_CODE')["POP_30_44"] +dfBetrachtung.set_index('LAU_CODE')["POP_45_59"]
      pop_60=dfBetrachtung.set_index('LAU_CODE')["POP_45_59"]+dfBetrachtung.set_index('LAU_CODE')["POP_60_74"] +dfBetrachtung.set_index('LAU_CODE')["POP_75"]

      popGroupDistribution=[pop_0_14, pop_15_59, pop_60]

      for popGroupCount in popGroupDistribution:
        for GKZ, popCount in popGroupCount.to_dict().items():
          trafficCellDict[GKZ]

    if("inhabitants" in paramsToRead):
      df=pd.read_csv(pathPopulationAgeGroupsCSV, encoding = "ISO-8859-1", sep=';',  na_values=['NA'])
      # print(df.head())
      # print(dfGemList.head())
      dfBetrachtung=df[df["LAU_CODE"].isin(dfGemList["GKZ"])]

      pop_total=dfBetrachtung.set_index('LAU_CODE')["POP_TOTAL"]
      # print(pop_total.to_dict().keys())

      for cellID, cell in trafficCellDict.items():
        cell.inhabitants=pop_total.to_dict()[cellID]
        

def AttributeReaderCSV(cellID, popGroup, paramToRead):

  #---read agegroups
  if paramToRead is "agegroup":
    df=pd.read_csv(pathPopulationAgeGroupsCSV, encoding = "ISO-8859-1", sep=';',  na_values=['NA'])
    dfBetrachtung=df.set_index('LAU_CODE')
    agegroupCount = defaultdict(int)

    for agegroupe in popGroup.possibleAttributes[paramToRead]:
      print(agegroupe)
      agegroupeSum=0
      
      for dataColumNames in list(dfBetrachtung):
        headSplit=dataColumNames.split("_") 

        if headSplit[0] == "POP" and headSplit[1].isdigit():
        #group in data is completle in the defined group)
          if int(headSplit[1]) >= agegroupe[0] and ((int(headSplit[2]) <= agegroupe[1]) if len(headSplit)>2 else int(headSplit[1]) <= agegroupe[1]):
            agegroupeSum=agegroupeSum+ dfBetrachtung.loc[cellID][dataColumNames]
          #group in data is a part of the defined group
          elif int(headSplit[1]) >= agegroupe[0] and int(headSplit[1]) < agegroupe[1]:
            upperBound= int(headSplit[2]) if len(headSplit)>2 else agegroupe[1]
            grouppart=dfBetrachtung.loc[cellID][dataColumNames]/(upperBound-int(headSplit[1]))*(agegroupe[1]-int(headSplit[1]))
            agegroupeSum = agegroupeSum + grouppart
          elif  int(headSplit[1]) < agegroupe[0] and ((int(headSplit[2])>agegroupe[0]) if len(headSplit)>2 else True):
            upperBound= int(headSplit[2]) if len(headSplit)>2 else agegroupe[1]
            grouppart=dfBetrachtung.loc[cellID][dataColumNames]/(upperBound-int(headSplit[1]))*(upperBound-agegroupe[0])
            agegroupeSum = agegroupeSum + grouppart
      agegroupCount[agegroupe]=agegroupeSum
    # print(agegroupCount)
    return agegroupCount  

  #---read gender
  if paramToRead is "gender":
    df=pd.read_csv(pathPopulationSexCSV, encoding = "ISO-8859-1", sep=';',  na_values=['NA'])
    dfBetrachtung=df.set_index('LAU_CODE')
    genderCount = defaultdict(int)
    genderCorresponding={"male":"MEN", "female":"WOMEN"}

    for gender in popGroup.possibleAttributes[paramToRead]:
      print(gender)

      for dataColumNames in list(dfBetrachtung):
        headSplit=dataColumNames.split("_")
   
        if headSplit[0] == "POP" and headSplit[1] == genderCorresponding[gender]:
          genderCount[gender] = dfBetrachtung.loc[cellID][dataColumNames]
  
    return genderCount

  #---read employment rate
  if paramToRead is "employment":
    df=pd.read_csv('Data/OGDEXT_AEST_GEMTAB_1.csv', sep=';',  na_values=['NA'], decimal=',' )
    df2=df[df["JAHR"]==df["JAHR"].max()]
    dfBetrachtung=df2.set_index('GCD')
    employmentCorresponding={"employment":"EWTQ_15BIS64"}

    employmentRate={"employmentRate_15_64": float(dfBetrachtung.loc[cellID][employmentCorresponding[paramToRead]])}
    return employmentRate

#---read human behavior in traffic
def behaviorReaderDummy(paramToRead, possibleAttributes):
  #--- read travel time budget
  if (paramToRead == "travelTimeBudget"):
    ttbSchweizerMikriozenzus={(6,24):(88.61,90.19,91.77), (25,64):(94.91,96.02,97.13),(65,100):(72.89,74.81,76,64)}
    ttbAgegroups=defaultdict()

    #-- chose data with smallest difference
    for agegroup in possibleAttributes["agegroup"]:
      keyForSmalestDifference=None
      smallestDifference = None
      for key in ttbSchweizerMikriozenzus.keys():
          diff=math.pow(agegroup[0]-key[0] ,2) + math.pow(agegroup[1]-key[1] ,2)
          if keyForSmalestDifference == None:
              keyForSmalestDifference=key
              smallestDifference = diff
          elif smallestDifference>diff:
              keyForSmalestDifference=key
              smallestDifference = diff
      ttbAgegroups[agegroup]=ttbSchweizerMikriozenzus[key]
    
    return ttbAgegroups
    
    





    
