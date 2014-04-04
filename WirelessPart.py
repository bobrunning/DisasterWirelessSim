import random
import simpy
import math


class TimeToFailure(object):
    def __init__(self,env,birthdate, distribution = "exponential"):
        self.env = env
        self.birthdate = birthdate
        self.distribution = distribution

    def getTTF(self,parm):
        if self.distribution == "exponential":
            return self.exponential(parm)
        else:
            print "error in distribution selection"

    def exponential(self,failurerate):
        return random.expovariate(failurerate)
        



class Dependency(object):
    def __init__(self, cellsite, dependic = { "root": 1}):
        self.cellsite = cellsite
        self.dependic = dependic # dict is name, percentload, and status

    def __str__(self):
        return "dependencies: " + str(self.dependic)

    def status(self):
        dependstatus = list()
        for key, dependency in self.dependic.items():
            if self.cellsite.partstatus.has_key(key) and self.cellsite.partstatus[key] != 1: #select only records where the cell is not inservice
                dependstatus.append(dependency)
                #print "add to dependency loop"

        dependsum = sum(dependstatus)
        dependsum = round(dependsum, 1)
        return dependsum



    def checkdependency(self, partstatus2):
        dependsum = self.status()
        if dependsum >= 1: #if sum is 1 then all conditions to require self turned off are correct
            return 4
        elif partstatus2 != 2:
            return 1
        else:
            return partstatus2

    def changestatus(self,dependency,status):
        self.dependic[dependency] = (self.dependic[dependency][0], status)
        return


class Part(object):
    def __init__(self, parent, env, nfe, name = "devicename", number = 0, partnumber = "rasp", rev = "a", firmware = "1C", software = "linux", reliability = .99999,mttr = 3600, dependency = Dependency(1)):
        self.name = name
        self.parent = parent # 0 = OFFL, 1=INSV, 2 = Fail, 3 reduced capacity; 4 offl due to dependent offl, 99 error in code
        self.dependency = dependency
        self.number = number
        self.partnumber = partnumber
        self.env = env
        self.nfe = nfe
        self.rev = rev
        self.firmware = firmware
        self.software = software
        self.reliability = reliability
        self.mttr = mttr
        #self.mttr = 10 #Number of clock cycles for the part to be fixed, there is a distribution
        self.partprocess = self.env.process(self.workingloop(self.nfe))
        self.breakprocess = self.env.process(self.break_machine())
        self.timetofail = TimeToFailure(self.env,1,distribution = "exponential")


    def __str__(self):
        return "Device Name: " + self.name +" Number: " + str(self.siteid) + " Part# " + self.partnumber + " rev: " + self.rev + " Firmware: " + self.firmware + " Reliability: " + str(self.reliability)


    def workingloop(self, nfe):
        """Do normal work as long as the simulation is running.

        If system breaks request a NFE

        """
        while True:
            try:
                # Normal loop while cell is workingworking part, measure  each time period
                #self.status = 1
                self.working()
                self.parent.partstatus[self.name] = self.watchdog()
                yield self.env.timeout(1)

            except simpy.Interrupt:
                self.parent.partstatus[self.name] = 2
                print "part failed: ", self.name
                # Request an NFE. This will preempt its "other_job".
                # Note Other work does not work
                with nfe.request(priority=1) as req:
                    yield req
                    #req.parameters[req.users]
                    #print nfe.parameters[req]
                    print self.parent.name," ", self.parent.equipmentid, ' called NFE: ' + str(self.env.now), " at this time"
                    yield self.env.timeout(self.mttr)
                print "NFE part fixed: ", self.name, " expected mttr ", self.mttr
                self.parent.partstatus[self.name] = 1

    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            yield self.env.timeout(self.time_to_failure())
            if self.parent.partstatus[self.name] == 1: #1 is inservice part
            # Only break the part if it is currently working.
                self.partprocess.interrupt()

    def working(self):
        return


    def time_to_failure(self):
        """Return time until next failure for a machine."""
        #return random.expovariate(1-self.reliability)
        return self.timetofail.getTTF(1-self.reliability)

    def watchdog(self):
        status = self.dependency.checkdependency(self.parent.partstatus[self.name])
        return status



class ConsumptionPart(Part):
    def __init__(self, parent, env, nfe, name = "devicename", number = 0, partnumber = "rasp", rev = "a", firmware = "1C", software = "linux", reliability = .99999,dependency = Dependency(1),capacity = 100):
        Part.__init__(self, parent, env, nfe, name, number, partnumber, rev, firmware, software, reliability,dependency)
        self.container = simpy.Container(env, capacity = capacity, init=capacity) #Note capacity is in tics
        self.fillprocess = self.env.process(self.checklevel())
        self.fillrate = 1


    def working(self):
        if self.container.level >= 1:
            #yield self.container.get(1)
            self.container.get(1)
            print "Time:", str(self.env.now), self.parent.siteid, self.name, " is at current level of " , self.container.level, " with a capacity of ", self.container.capacity

    def fillpart(self):
        status = self.dependency.status()
        #print "fill status "
        if status == 0: #0 means dependency not out of service
            #print "filling container"
            diff = self.container.capacity - self.container.level
            #print "container capacity " , self.container.capacity, " container level ", self.container.level
            if diff >= self.fillrate:
                #yield self.container.put(self.fillrate - self.fillrate % diff)
                self.container.put(self.fillrate)
            else:
                self.container.put(math.ceil(self.fillrate-diff))

        else:
            pass
            #print "not filling container"



    def checklevel(self):
        while True:
            self.fillpart()
            if self.container.level < 1:
                self.parent.partstatus[self.name] = 2
            else:
                self.parent.partstatus[self.name] = 1

            yield self.env.timeout(1)

