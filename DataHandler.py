import csv
import numpy as np 
import pandas as pd 
from collections import defaultdict

#Filepaths
pathTrafficCellsCSV = './Data/Gemeinde_Liste_V1.csv'
pathPopulationAgeGroupsCSV='Data/STMK_01012017_AGE.csv'

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
      print(pop_total.to_dict().keys())

      for cellID, cell in trafficCellDict.items():
        cell.inhabitants=pop_total.to_dict()[cellID]
        

 
