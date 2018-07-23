import pandas as pd 
import numpy as np
from collections import defaultdict 



class TrafficCell():

    def __init__(self, name, cellID):
        self._name=name
        self.inhabitants=int()
        self.popGroups=None
        self.cellID=cellID
        

        self.populationParams=None
        self.attractivity=None
    
    
    def __str__(self):
        return str(self._name)
        

    def SetPopulationParams(self,populationParams):
        self.populationParams=populationParams


