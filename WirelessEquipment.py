#Analysis of cell site reliability
###
import numpy as np
import simpy
import random
import csv
import math
from WirelessPart import *

class GroupofParts(object):
    def __init__(self, env, nfe, equipmentid = "000000",equipmenttype = "equipmenttypelabel",latitude = 0,longitude = 0,name = "cellsite",zlocation="MCRD"):
        self.equipmentid = equipmentid
        self.equipmenttype = equipmenttype
        self.latitude = latitude
        self.nfe = nfe
        self.env = env
        self.longitude = longitude
        self.name = name
        #self.siteid = siteid
        self.zlocation = zlocation
        self.parts = dict()
        self.partstatus = dict()
        self.cellprocess = self.env.process(self.checkpartstatus())
        self.data = []

    def __str__(self):
        return "equipmentid: " + self.equipmentid + " Equipmenttype " + self.equipmenttype + " Latitude: " + str(self.latitude) + " Longitude: " + str(self.longitude) + " Name: " + self.name

    def updatestatus(self):
        rerun = False
        print "updatestart"
        #Check each part and update the status dictionary
        for key, part in self.parts.iteritems():
            if self.partstatus.has_key(key) != True:
                self.partstatus.update({key:1})

    def addpart(self,key, part):
        self.parts.update({key:part})


    def addparttest(self):
        self.parts.update({"Generator":Part(self,self.env,self.nfe,"Generator",reliability = .99999,dependency = Dependency(self,{"root": 1}))})
        self.parts.update({"BatteryLevel":ConsumptionPart(self,self.env,self.nfe,"BatteryLevel",reliability = .99999,dependency = Dependency(self,{"Generator": 1}),capacity = 5)})
        self.parts.update({"Battery":Part(self,self.env,self.nfe,"Battery",reliability = .999999,dependency = Dependency(self,{"root":1}))})
        self.parts.update({"CSR":Part(self,self.env,self.nfe,"CSR",reliability = .99999,dependency = Dependency(self,{"Battery": 1,"BatteryLevel":1,"External":1}))})
        self.parts.update({"RRU1":Part(self,self.env,self.nfe,"RRU1",dependency = Dependency(self,{"CSR": 1}),reliability = .99999)})
        self.parts.update({"RRU2":Part(self,self.env,self.nfe,"RRU2",dependency = Dependency(self,{"CSR": 1}))})
        self.parts.update({"RRU3":Part(self,self.env,self.nfe,"RRU3",dependency = Dependency(self,{"CSR": 1}))})
        self.parts.update({"Antenna1":Part(self,self.env,self.nfe,"Antenna1",reliability = .9999999,dependency = Dependency(self,{"RRU1": 1}))})
        self.parts.update({"Antenna3":Part(self,self.env,self.nfe,"Antenna3",reliability = .9999999,dependency = Dependency(self,{"RRU3": 1}))})
        self.parts.update({"Antenna2":Part(self,self.env,self.nfe,"Antenna2",reliability = .9999999,dependency = Dependency(self,{"RRU2": 1}))})
        self.parts.update({"Cellsite":Part(self,self.env,self.nfe,"Cellsite",reliability = .9999999999,dependency = Dependency(self,{"Antenna1": .333333,"Antenna2": .333333,"Antenna3": .333333}))})
        print(self.parts)

        return

    def updatextdep(self, key, status):
        if self.partstatus.has_key(key) != True:
            self.partstatus[key] = status
        else:
            self.partstatus.update({key:status})

        return
        

    def checkpartstatus(self):
        while True:
            x = [self.equipmentid, self.env.now]
            for key, part in self.parts.items():
                print "Time: " + str(self.env.now) + " " + self.equipmentid + " " + part.name + " " + str(self.partstatus[key])

            for key, part in self.parts.items():
                x.append(part.name)
                x.append(self.partstatus[key])
            self.data.append(x)
            yield self.env.timeout(1) #If I move this to the top of the loop it will be behind the part by one tic


    def createpart(self, env, nfe, name = "devicename", number = 0, partnumber = "rasp", rev = "a", firmware = "1C", software = "linux", reliability = .99999,dependency = ["None"]):
        #create it so that if dependency is not a list it will be forced to a list
        self.parts.append(Part(self.env,self.nfe,name,number, partnumber,rev,firmware,software,reliability,dependency))
        return

    def cleardata(self):
        self.data = []
        return

        

class CellSite(GroupofParts):
    def __init__(self, env, nfe, equipmentid = "0000", equipmenttype = "equipmenttypelabel", siteid = "000000",latitude = 0,longitude = 0,name = "cellsite",zlocation="MCRD"):
        GroupofParts.__init__(self, env, nfe, equipmentid,equipmenttype,latitude,longitude,name,zlocation)
        self.siteid = siteid

    def __str__(self):
        return "siteid: " + self.siteid + " " + "Latitude: " + str(self.latitude) + " Longitude: " + str(self.longitude) + " Name: " + self.name


    def addparttest(self):
        self.parts.update({"Generator":Part(self,self.env,self.nfe,"Generator",reliability = .99999,dependency = Dependency(self,{"root": 1}))})
        self.parts.update({"BatteryLevel":ConsumptionPart(self,self.env,self.nfe,"BatteryLevel",reliability = .99999,dependency = Dependency(self,{"Generator": 1}),capacity = 5)})
        self.parts.update({"Battery":Part(self,self.env,self.nfe,"Battery",reliability = .999999,dependency = Dependency(self,{"root":1}))})
        self.parts.update({"CSR":Part(self,self.env,self.nfe,"CSR",reliability = .99999,dependency = Dependency(self,{"Battery": 1,"BatteryLevel":1,"chrtr0":1}))})
        self.parts.update({"RRU1":Part(self,self.env,self.nfe,"RRU1",dependency = Dependency(self,{"CSR": 1}),reliability = .99999)})
        self.parts.update({"RRU2":Part(self,self.env,self.nfe,"RRU2",dependency = Dependency(self,{"CSR": 1}))})
        self.parts.update({"RRU3":Part(self,self.env,self.nfe,"RRU3",dependency = Dependency(self,{"CSR": 1}))})
        self.parts.update({"Antenna1":Part(self,self.env,self.nfe,"Antenna1",reliability = .9999999,dependency = Dependency(self,{"RRU1": 1}))})
        self.parts.update({"Antenna3":Part(self,self.env,self.nfe,"Antenna3",reliability = .9999999,dependency = Dependency(self,{"RRU3": 1}))})
        self.parts.update({"Antenna2":Part(self,self.env,self.nfe,"Antenna2",reliability = .9999999,dependency = Dependency(self,{"RRU2": 1}))})
        self.parts.update({"Cellsite":Part(self,self.env,self.nfe,"Cellsite",reliability = .9999999999,dependency = Dependency(self,{"Antenna1": .333333,"Antenna2": .333333,"Antenna3": .333333}))})
        self.parts.update({"chrtr0":Part(self,self.env,self.nfe,"chrtr0",reliability = .99999999999, dependency = Dependency(self,{"root": 1}))})
        print(self.parts)

        return



class NFE(simpy.resources.resource.PreemptiveResource):
    def __init__(self, env, capacity = 10,names=[]):
        simpy.resources.resource.Resource.__init__(self, env,capacity = capacity)
        self.env = env
        self.names = names
        self.location = []
        self.parameters = dict()
        #self.addname()
        #self.workingprocess = self.env.process(self.work(priority = 5))
        #Priority 5 is idle, 4 is low priority, 3 Severity three, 2 severity two, 1 severity one, 0 is unable to work
        self.low = 0
        self.period = 1

        
    def addname(self):
        for indx, val in enumerate(self.users):
            print indx, val
            self.parameters.update({val:[self.names[indx],0.0000,0.0000]})
        
    def hi(self):
        print "hi"


    def work(self,priority):
        while True:
            #Keep working until work is done or interupted
            with self.request(priority = priority) as req:
                self.addname()
                print "req ", req, "test", self.parameters[req]
                yield req
                try:
                    yield env.timeout(self.period)
                    self.low += self.period
                    #print self.name, " doing ", priority, " level work"
                except simpy.Interrupt:
                    pass
                    #print self.name, " interrupt work"

    def travel(self,destlocation=[]):
        #Time to trave to the cell in question
        return 1



class Engineer():
    def __init__(self, env, capacity = 1, name = "Bill",location = ()):
        self.env = env
        self.capacity = 1
        self.name = name
        self.location = location
        self.nfe = simpy.PreemptiveResource(env, capacity=capacity)
        self.workingprocess = self.env.process(self.work(priority = 5))
        #Priority 5 is idle, 4 is low priority, 3 Severity three, 2 severity two, 1 severity one, 0 is unable to work
        self.low = 0
        self.period = 1
        
    # create a resource with a single capacity
    # We start work with that resource on a low priority
    # Work can be interupted by a higher priority
    # Find a way to prevent high priority work from interuption high priority work

    def work(self,priority):
        while True:
            #Keep working until work is done or interupted
            with self.nfe.request(priority = priority) as req:
                yield req
                try:
                    yield env.timeout(self.period)
                    self.low += self.period
                    print self.name, " doing ", priority, " level work"
                except simpy.Interrupt:
                    print self.name, " interrupt work"
    


if __name__ == '__main__':

    def simtofile(env,item):
        while True:
            yield env.timeout(1000)
            for x in item:
                with open("simoutput.csv", "ab") as f:
                    writer = csv.writer(f)
                    writer.writerows(x.data)
                print "data written"
                x.cleardata()

    def updatelinkedparts(env):
        while True:
            yield env.timeout(1)
            #This works but requires all connections to be individually coded
            #
            cell[0].partstatus[ethernet[0].equipmentid] = ethernet[0].partstatus[ethernet[0].name]
            cell[0].partstatus[power[0].equipmentid] = power[0].partstatus[power[0].name]

        pass


    env = simpy.Environment()
    random.seed(2234259)
    #nfe = simpy.PreemptiveResource(env, capacity=5)
    nfe = NFE(env,capacity = 5,names = ["Bill","Jill","Mill","Hill","Will"])
    #eng = Engineer(env)
    cell = []
    ethernet = []
    power = []


    for name in range(0,1,1):
        item = GroupofParts(env,nfe,equipmentid="Alliant" + str(name),equipmenttype="Power",name="Power")
        part = Part(item,env,item.nfe,"Power",reliability = .99,dependency = Dependency(item,{"root":1}))
        item.addpart("Power",part)
        item.updatestatus()
        power.append(item)
        

    for name in range(0,1,1):
        item = GroupofParts(env,nfe,equipmentid="Chrtr" + str(name),equipmenttype="Ethernet",name="Fiber")
        part = Part(item,env,item.nfe,"Fiber",reliability = .99999999,dependency = Dependency(item,{"root":1}))
        item.addpart("Fiber",part)
        item.updatestatus()
        ethernet.append(item)


    for site in range(764090,764100,10):
        item = CellSite(env,nfe,equipmentid = "Cell" + str(site))
        item.addpart("PropaneLevel", ConsumptionPart(item,env,item.nfe,"PropaneLevel",reliability = .99999,dependency = Dependency(item,{"Alliant0":1}),capacity = 5))
        item.addpart("Generator", Part(item,env,item.nfe,"Generator",reliability = .99999,dependency = Dependency(item,{"PropaneLevel": 1})))
        item.addpart("BatteryLevel", ConsumptionPart(item,env,item.nfe,"BatteryLevel",reliability = .99999,dependency = Dependency(item,{"Generator": 1}),capacity = 5))
        item.addpart("Battery", Part(item,env,item.nfe,"Battery",reliability = .999999,dependency = Dependency(item,{"root":1})))
        item.addpart("CSR", Part(item,env,item.nfe,"CSR",reliability = .99999,dependency = Dependency(item,{"Battery": 1,"BatteryLevel":1,"Chrtr0":1})))
        item.addpart("RRU1", Part(item,env,item.nfe,"RRU1",dependency = Dependency(item,{"CSR": 1}),reliability = .99999))
        item.addpart("RRU2", Part(item,env,item.nfe,"RRU2",dependency = Dependency(item,{"CSR": 1})))
        item.addpart("RRU3", Part(item,env,item.nfe,"RRU3",dependency = Dependency(item,{"CSR": 1})))
        item.addpart("Antenna1", Part(item,env,item.nfe,"Antenna1",reliability = .9999999,dependency = Dependency(item,{"RRU1": 1})))
        item.addpart("Antenna3", Part(item,env,item.nfe,"Antenna3",reliability = .9999999,dependency = Dependency(item,{"RRU3": 1})))
        item.addpart("Antenna2", Part(item,env,item.nfe,"Antenna2",reliability = .9999999,dependency = Dependency(item,{"RRU2": 1})))
        item.addpart("Cellsite", Part(item,env,item.nfe,"Cellsite",reliability = .9999999999,dependency = Dependency(item,{"Antenna1": .333333,"Antenna2": .333333,"Antenna3": .333333})))
        item.addpart("Chrtr0", Part(item,env,item.nfe,"Chrtr0",reliability = .99999999999, dependency = Dependency(item,{"root": 1})))
        item.addpart("Alliant0", Part(item,env,item.nfe,"Alliant0",reliability = .99999999999, dependency = Dependency(item,{"root": 1})))

        item.updatestatus()
        cell.append(item)

    env.process(simtofile(env,cell))
    env.process(simtofile(env,ethernet))
    env.process(updatelinkedparts(env))
    print cell
    #env.step()
    nfe.addname()
  #  env.run(until = 1)


    env.run(until = 3)
