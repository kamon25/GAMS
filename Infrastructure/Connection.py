class Connection():
    
    def __init__(self , start_node, end_node, connectionType, distance, losData, capacity ):
        self.start_node = start_node
        self.end_node = end_node
        self.distance = distance
        self.losData = losData
        self.weight = distance #initial weight
        self.capacity = capacity #trips per hour
        self.stepLoad=[]

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
        if len(self.stepLoad)> step:
            self.stepLoad[step] += trips
        else:
            self.stepLoad.append(trips)

    def setOccupancy(self,tripsAtConnection, peakHours):
        self.occupancy = tripsAtConnection/(self.capacity*peakHours)
        

 
