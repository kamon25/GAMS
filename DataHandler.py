import csv
import numpy as np 
import pandas as pd 
from collections import defaultdict

#Filepaths
pathTrafficCellsCSV = "./Data/Gemeinde_Liste_V1.csv"

def TrafficCellReaderCSV():

    towns = defaultdict()
    with open(pathTrafficCellsCSV) as f:
      reader = csv.reader(f, delimiter=';')
      skip = True
      for row in reader:
        if(skip):
          skip = False
          continue      
        
        towns[row[0]] = row[1]
    
    return towns

def inhabitantReader():
    pass



