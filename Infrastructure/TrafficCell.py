import pandas as pd 
import numpy as np 



class TrafficCell():

    def __init__(self, name, cellID):
        self._name=name
        self.inhabitants=None
        self.cellID=cellID

        self.populationParams=None
        self.attractivity=None
    
    
    def __str__(self):
        return str(self._name)
        

    def SetPopulationParams(self,populationParams):
        self.populationParams=populationParams


