import csv
import pandas as pd
from WirelessEquipment import *
import simpy
import random
import re
import string
import math

###########################################################
#Helper functions

def simtofile(env,item):
    while True:
        yield env.timeout(1000)
        for k in item.keys():
            with open("simoutput.csv", "ab") as f:
                writer = csv.writer(f)
                writer.writerows(item[k].data)
            print "data written"
            item[k].cleardata()

def updatelinkedparts(env):
    while True:
        yield env.timeout(1)
        #This works but requires all connections to be individually coded
        #
        cell[0].partstatus[ethernet[0].equipmentid] = ethernet[0].partstatus[ethernet[0].name]
        cell[0].partstatus[power[0].equipmentid] = power[0].partstatus[power[0].name]

    pass


def getdata(filename):
    x = []
    
    with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            x.append(row)

    names = x.pop(0)
    names = [re.sub(r"[ ()-.@]","",y) for y in names]

    df = pd.DataFrame(x,columns = names)
    return df


###############################################################
env = simpy.Environment()
random.seed(2234259)
nfe = NFE(env,capacity = 5,names = ["Bill","Jill","Mill","Hill","Will"])
mttr = 3600
mttr_batt = 3600 * 24
mttr_ant = 3600 * 12
mttr_gen = 3600 * 12
r_enodeb = .99999
r_rru = .99999
r_ant = .99999
r_gen = .99985 #Generator reliability Ayers book page 195
c_gen = [4,1] #slot 0 is alpha, slot 1 is beta - Used to calculate generator fuel level
 # See R miscSim.R - with alpha being 4, and beta 1, 60% of all generators have a fuel level of >80% - Seems to be a tight level
 # Alpha 1, beta 1 is 40% of all generators have a fuel level of 40%, 50/50, 60/60.... very loose refueling level

cellsites = {}

celldf = getdata('celllist2013-2.csv')


print celldf.SiteName

#Build cellsite shell
for i, row in celldf.iterrows():
    cell = CellSite(env,nfe,siteid = row.SiteNum,latitude = row.Latitude,equipmentid = row.SiteNum,
                         longitude = row.Longitude,name = row.SiteName,zlocation = "MCRD")
    cell.addpart("EnodeB",Part(cell,env,cell.nfe,"EnodeB",reliability = r_enodeb, mttr = mttr, dependency = Dependency(cell,{"CSR": 1})))
    cell.addpart("RRU1", Part(cell,env,cell.nfe,"RRU1",reliability = r_rru, mttr = mttr, dependency = Dependency(cell,{"CSR": 1})))
    cell.addpart("RRU2", Part(cell,env,cell.nfe,"RRU2",reliability = r_rru, mttr = mttr, dependency = Dependency(cell,{"CSR": 1})))
    cell.addpart("RRU3", Part(cell,env,cell.nfe,"RRU3",reliability = r_rru, mttr = mttr, dependency = Dependency(cell,{"CSR": 1})))
    cell.addpart("Antenna1", Part(cell,env,cell.nfe,"Antenna1",reliability = r_ant,mttr = mttr_ant, dependency = Dependency(cell,{"RRU1": 1})))
    cell.addpart("Antenna3", Part(cell,env,cell.nfe,"Antenna3",reliability = r_ant,mttr = mttr_ant, dependency = Dependency(cell,{"RRU3": 1})))
    cell.addpart("Antenna2", Part(cell,env,cell.nfe,"Antenna2",reliability = r_ant,mttr = mttr_ant, dependency = Dependency(cell,{"RRU2": 1})))
    cell.addpart("Cellsite", Part(cell,env,cell.nfe,"Cellsite",reliability = .9999999999,mttr = 1, dependency = Dependency(cell,{"Antenna1": .333333,"Antenna2": .333333,"Antenna3": .333333})))
    cell.addpart("BatteryLevel", ConsumptionPart(cell,env,cell.nfe,"BatteryLevel",reliability = .9999999999,mttr = 1,dependency = Dependency(cell,{"root": 1}),capacity = 5))
    cell.addpart("Battery", Part(cell,env,cell.nfe,"Battery",reliability = .999999, mttr = mttr_batt, dependency = Dependency(cell,{"root":1})))
    cell.addpart("CSR", Part(cell,env,cell.nfe,"CSR",reliability = .99999,mttr = mttr, dependency = Dependency(cell,{"Battery": 1,"BatteryLevel":1,"Backhaul":1})))

    #cellsites.update(cell)
    cellsites[str(row.SiteNum)] = cell



######################################################
#Add enode parts
enodebdf = getdata('enodeb.csv')

for i, row in enodebdf.iterrows():
    if cellsites.has_key(str(row.Site_Number)):
        cellsites[str(row.Site_Number)].parts["EnodeB"].partnumber = row.eNodeBType

#######################################################
#Add batteries and generator
batterydf = getdata('battery1.csv')

for i, row in batterydf.iterrows():
    if cellsites.has_key(str(row.SiteID)):
        batterycap = float(row.battery1) * 3600 + 1 #60 minutes * 60 seconds, add one second to ensure no zeros
        cellsites[row.SiteID].parts["BatteryLevel"].container = simpy.Container(env, capacity = batterycap, init=batterycap)


generatordf = getdata('GeneratorReport.csv')

for i, row in generatordf.iterrows():
    if cellsites.has_key(str(row.Site_Number)):
        cellsites[row.Site_Number].addpart("Generator", Part(cellsites[row.Site_Number],env,cellsites[row.Site_Number].nfe,"Generator",
                                                        partnumber = row.GeneratorModel,
                                                        reliability = r_gen, mttr = mttr_gen
                                                        dependency = Dependency(cellsites[row.Site_Number],{"FuelLevel": 1})))
        fuellevel = float(row.GeneratorEstimatedRuntimeHrs) * 3600 + 1 #3600 seconds in an hour + 1 second to ensure never zero
        fuellevel = fuellevel * random.betavariate(c_gen[0],c_gen[1])
        fuellevel = math.ceil(fuellevel)
        

        cellsites[row.Site_Number].addpart("FuelLevel", ConsumptionPart(cellsites[row.Site_Number],env,cellsites[row.Site_Number],"FuelLevel",
                                                        reliability = .9999999999,mttr = mttr_gen, partnumber = row.FuelTypeDescription,
                                                        dependency = Dependency(cellsites[row.Site_Number],{"root":1}),
                                                        capacity = fuellevel))


    

#######################################################
#Need to update all parts before simulation starts
for cell in cellsites.itervalues(): cell.updatestatus()


#In the parts class add a start to constructor, then a method to start the process, 0 is offl, 1 is start
#move the env process start to the start method
#change the add part for generator to 0 for start
#figure out how to have a dependency start a system


env.process(simtofile(env,cellsites))
#env.process(simtofile(env,ethernet))
#env.process(updatelinkedparts(env))
print cell
#env.step()
#nfe.addname()
env.run(until = 1814400)


#env.run(until = 3000)

