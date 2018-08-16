import random




class Inhabitant():
    # static variables:
    femalecounter=0
    
    
    def setAgegroupe(self, i, trafficcellInhabitants , agegroupValues):
        sumOfGroups = 0
        for value in agegroupValues.values():
            sumOfGroups = sumOfGroups + value
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as Inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            sumOfGroups = 0
            for key, value in agegroupValues.items():
                if i >= sumOfGroups:
                    self.agegroupe = key
                    #print(key)
                    break
                else:
                    sumOfGroups = sumOfGroups + value  
        else:
            raise NotImplementedError("Implement setAgegroupmethod -> inhabitants != sum of Agegroups")

    def setGender(self, i, trafficcellInhabitants, genderDistribution):        
        sumOfGroups = 0
        if i == 0: Inhabitant.femalecounter=0
        for value in genderDistribution.values():
            sumOfGroups = sumOfGroups + value
        #print("Summe der Gruppe: " + str(sumOfGroups))
        #print("set as inhabitants: " + str(trafficcellInhabitants))
        if sumOfGroups == trafficcellInhabitants:
            radomnumberGender = random.randint(0, trafficcellInhabitants)
            if genderDistribution["male"]<=radomnumberGender or Inhabitant.femalecounter==genderDistribution["female"]:
                self.gender="male"                
            else:
                self.gender="female"
                Inhabitant.femalecounter=Inhabitant.femalecounter+1
        else:
            raise NotImplementedError("Implement setGender -> inhabitants != sum of genderGroups")

    def setEmployment(self, i , employmentRate, grouplist):
        #-- is employment possible (ageroupe)? 
        employmentPossible=False
        for group in grouplist:
            if group._attributes["agegroup"] ==self.agegroupe and group._attributes["employment"]=="employed":
                employmentPossible=True
        
        if employmentPossible:
            randomnumberEmployment=random.randrange(0,1,0.001)
            if randomnumberEmployment<=employmentRate:
                self.employment="employed"
            else:
                self.employment="unemployed"
        else:
            self.employment="unemployed"