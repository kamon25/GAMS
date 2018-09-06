class Connection():
    
    def __init__(self , start_node, end_node, connectionType, distance, losData, capacity ):
        self.start_node = start_node
        self.end_node = end_node
        self.distance = distance
        self.losData = losData
        self.weight = distance #initial weight
        self.capacity = capacity #trips per hour
        self.stepLoad = []
        self.occupancy = []

        #Split connection type
        self.mode= connectionType.split("_")[0]
        self.infrastructure = connectionType.split("_")[1]
    
    def getConnectionType(self):
        tempstring = self.mode + '_' + self.infrastructure
        return tempstring
    
    def setWeight(self, weight):
        self.weight = weight
    
    def calcWeightGlobalFactors(self, factor):
        self.weight *= factor
    
    def setStepLoad(self, trips, step):
        if len(self.stepLoad) > step:
            self.stepLoad[step] += trips
            self.occupancy[step] = self.stepLoad[step]/self.capacity

        else:
            self.stepLoad.append(trips)
            self.occupancy.append(trips/self.capacity)
    
    def toDict(self, step):
        outputDict={
            "source": self.start_node,
            "target": self.end_node,
            "infra": self.getConnectionType(),
            "weight": self.weight,
            "stepLoad": self.stepLoad[step],
            "occupancy": self.occupancy[step],
            "capacity": self.capacity
            }
        
        return outputDict




 
