import random
import numpy as np
from collections import defaultdict




class Inhabitant():
    # static variables:
    femalecounter=0

    # Constant Number of Trips to Work
    tripRateWork=1.35 #Schweizer Mikrozensus

    def __init__(self):
        self.attributes=defaultdict()
    
    
    def setAgegroupe(self, i, trafficcellInhabitants , agegroupValues, agegroupKey):
        sumOfGroups = 0
        for value in agegroupValues.values():
            sumOfGroups = sumOfGroups + value
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as Inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            sumOfGroups = 0
            for key, value in agegroupValues.items():
                if i >= sumOfGroups:
                    self.attributes[agegroupKey] = key
                    #print(key)
                    break
                else:
                    sumOfGroups = sumOfGroups + value  
        else:
            raise NotImplementedError("Implement setAgegroupmethod -> inhabitants != sum of Agegroups")


    def setGender(self, i, trafficcellInhabitants, genderDistribution, genderKey): #maybe subsitute keys        
        sumOfGroups = 0
        if i == 0: Inhabitant.femalecounter=0
        for value in genderDistribution.values():
            sumOfGroups = sumOfGroups + value
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            radomnumberGender = random.randint(0, trafficcellInhabitants)
            if genderDistribution["male"]<=radomnumberGender or Inhabitant.femalecounter==genderDistribution["female"]:
                self.attributes[genderKey]="male"                
            else:
                self.attributes[genderKey]="female"
                Inhabitant.femalecounter=Inhabitant.femalecounter+1
        else:
            raise NotImplementedError("Implement setGender -> inhabitants != sum of genderGroups")

    def setEmployment(self, i , employmentRate, grouplist, employmentKey, agegroupKey):
        #-- is employment possible (ageroupe)? 
        employmentPossible=False
        for group in grouplist:
            if group._attributes[agegroupKey] == self.attributes[agegroupKey] and group._attributes[employmentKey]=="employed":
                employmentPossible=True
        
        if employmentPossible:
            randomnumberEmployment=random.randrange(0,1,0.001)
            if randomnumberEmployment<=employmentRate:
                self.attributes[employmentKey]="employed"
            else:
                self.attributes[employmentKey]="unemployed"
        else:
            self.attributes[employmentKey]="unemployed"
    
    def setTravelTimeBudget(self, i, timeBudgetAgegroups):
        self.travelTimeBudget = np.random.triangular(*timeBudgetAgegroups[self.attributes["agegroup"]])

    def setTripRate(self, i , tripRateAgegroups):
        self.tripRate = np.random.triangular(*tripRateAgegroups[ self.attributes["agegroup"]])
        self.tripRateWork = Inhabitant.tripRateWork
        