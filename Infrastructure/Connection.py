import math

class Connection():

    def __init__(self, start_node, end_node, connectionType, distance, losData, capacity, basicLoad):
        self.start_node = start_node
        self.end_node = end_node
        self.distance = distance
        self.losData = losData
        self.weight = distance  # initial weight
        self.globalWeightFactor = 1  # default 1
        self.capacity = capacity  # trips per hour
        self.stepLoad = []
        self.occupancy = []
        self.currentLos = 1 #default
        self.basicLoad = basicLoad #percentage

        # Split connection type
        self.mode = connectionType.split("_")[0]
        self.infrastructure = connectionType.split("_")[1]

    def getConnectionType(self):
        tempstring = self.mode + '_' + self.infrastructure
        return tempstring

    def setWeight(self, weight):
        self.weight = weight

    def setGlobalWeightFactors(self, factor, referenceSpeed):
        self.globalWeightFactor = factor
        self.referenceSpeed = referenceSpeed
        self.averageSpeedZero = referenceSpeed/factor

    def getWeight(self):
        return self.weight*self.globalWeightFactor

    def setStepLoad(self, trips, step):
        if len(self.stepLoad) > step:
            self.stepLoad[step] += trips*(1+self.basicLoad) 
            self.occupancy[step] = self.stepLoad[step]/self.capacity

        else:
            self.stepLoad.append(trips*(1+self.basicLoad))
            self.occupancy.append(trips/self.capacity)

        self.calcLos(step)
    
    def calcLos(self, step):
        #los=a*(M/C)^b
        # a and b should from LosData
        if self.mode == 'car':
            a=1.0
            b=6.0
            self.currentLos = a*math.pow(self.occupancy[step], b)
        elif self.mode == 'bus' or self.mode == 'train':
            a=1.0
            b=6.0
            self.currentLos = a*math.pow(self.occupancy[step], b)


    def toDict(self, step):
        outputDict = {
            "source": self.start_node,
            "target": self.end_node,
            "infra": self.getConnectionType(),
            "weight": self.getWeight(),
            "stepLoad": self.stepLoad[step],
            "occupancy": self.occupancy[step],
            "capacity": self.capacity
        }

        return outputDict
