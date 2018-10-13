import random
import numpy as np
from collections import defaultdict
import time


class Inhabitant():
    __slots__ = "attributes", "tripRate", "travelTimeBudget", "tripRateWork", "mobility"

    # static variables:
    femalecounter = 0

    # Constant Number of Trips to Work
    tripRateWorkSwiss = 1.35  # Schweizer Mikrozensus

    def __init__(self):
        self.attributes = defaultdict()

    def __str__(self):
        return "Here Inhabitant"

    def setAgegroupe(self, i, trafficcellInhabitants, agegroupValues, agegroupKey):
        sumOfGroups = sum(agegroupValues.values())
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as Inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            sumOfGroups = 0
            for key, value in agegroupValues.items():
                if i < sumOfGroups + value:
                    self.attributes[agegroupKey] = key
                    # print(key)
                    break
                else:
                    sumOfGroups = sumOfGroups + value
        else:
            sumOfGroups = 0
            for key, value in agegroupValues.items():
                if i < sumOfGroups + value:
                    self.attributes[agegroupKey] = key
                    # print(key)
                    break
                else:
                    sumOfGroups = sumOfGroups + value

    def setGender(self, i, trafficcellInhabitants, genderDistribution, genderKey):  # maybe subsitute keys
        sumOfGroups = sum(genderDistribution.values())
        femalecounter = Inhabitant.femalecounter
        if i == 0:
            femalecounter = 0
        maleFemaleRatio = genderDistribution["male"] / \
            genderDistribution["female"]
        # Version two with for
        # for key, value in genderDistribution.items():
        #     sumOfGroups = sumOfGroups + value
        #     if key == "female":
        #         maleFemaleRatio = maleFemaleRatio/value
        #     elif key == "male":
        #         maleFemaleRatio = maleFemaleRatio * value
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            if(femalecounter == 0):
                currentRatio = trafficcellInhabitants-1
            else:
                currentRatio = (i-femalecounter)/femalecounter

            if maleFemaleRatio > currentRatio or femalecounter == genderDistribution["female"]:
                self.attributes[genderKey] = "male"
            else:
                self.attributes[genderKey] = "female"
                femalecounter = femalecounter+1
            Inhabitant.femalecounter = femalecounter
        else:
            raise NotImplementedError(
                "Implement setGender -> inhabitants != sum of genderGroups")

    def setEmployment(self, i, employmentRate, groupDict, employmentKey, agegroupKey):
        # -- is employment possible (ageroupe)?
        employmentPossible = False
        for group in groupDict.values():  # for is not neccesary if possibilities are earlier
            if group._attributes[agegroupKey] == self.attributes[agegroupKey] and group._attributes[employmentKey] == "employed":
                employmentPossible = True
                break
            #print("Group" + str(group._attributes[agegroupKey]))
            #print("self" + str(self.attributes[agegroupKey] ))

        if employmentPossible:
            randomnumberEmployment = np.random.uniform()
            if randomnumberEmployment <= employmentRate/100.0:
                self.attributes[employmentKey] = "employed"
            else:
                self.attributes[employmentKey] = "unemployed"
        else:
            self.attributes[employmentKey] = "unemployed"

    def setCarAviable(self, i, carAviableRate, groupDict, carKey, agegroupKey, mobilityCarAvailable):
        carPossible = False
        for group in groupDict.values():
            if group._attributes[agegroupKey] == self.attributes[agegroupKey] and group._attributes[carKey] == 'available':
                carPossible = True
                break
        
        if carPossible:
            carProbability = carAviableRate[self.attributes[agegroupKey]]
            randomnumberCar = np.random.uniform()
            if randomnumberCar <= carProbability:
                self.attributes[carKey]='available'
                self.mobility = mobilityCarAvailable['available']
            else:
                self.attributes[carKey]='notAvailable'
                self.mobility = mobilityCarAvailable['notAvailable']
        else:
            self.attributes[carKey]='notAvailable'
            self.mobility = mobilityCarAvailable['notAvailable']
    
    def setCarAviableFromDensity(self, i, carDensity, trafficcellInhabitants, potentialCarUsers, groupDict, carKey, agegroupKey):
        # -- is a car aviability possible? possible (ageroupe)?
        carPossible = False
        for group in groupDict.values():
            if group._attributes[agegroupKey] == self.attributes[agegroupKey] and group._attributes[carKey] == 'available':
                carPossible = True
                break
        
        if carPossible:
            carProbability = (carDensity/1000.0)*trafficcellInhabitants/potentialCarUsers
            randomnumberCar = np.random.uniform()
            if randomnumberCar <= carProbability:
                self.attributes[carKey]='available'
            else:
                self.attributes[carKey]='notAvailable'
        else:
            self.attributes[carKey]='notAvailable'


    def setTravelTimeBudget(self, i, timeBudgetAgegroups):
        self.travelTimeBudget = np.random.triangular(
            *timeBudgetAgegroups[self.attributes["agegroup"]]) / 60 #  min -> h

    def setTripRate(self, i, tripRateAgegroups, jsonParameter):
        self.tripRate = np.random.triangular(
            *tripRateAgegroups[self.attributes["agegroup"]])
        self.tripRateWork = jsonParameter['tripRateWork']
    
 
