from ..db import dbConnection as db
from thundercloud.util.restApiClient import RestApiClient
from thundercloud.spec.slave import SlaveState
from thundercloud import config

from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from twisted.internet.task import LoopingCall

import logging
import copy
import math

log = logging.getLogger("orchestrator.slave")

# Slave perspective: send vanilla commands to slave servers
class SlavePerspective(object):
    def __init__(self, slaveSpec):
        self.slaveSpec = slaveSpec
    
    def url(self, path=None):
        if path is None:
            return str("%s://%s:%s/%s" % (self.slaveSpec.scheme, self.slaveSpec.host, self.slaveSpec.port, self.slaveSpec.path))
        else:
            if path[0] == "/":
                path = path[1:]
            return str("%s://%s:%s/%s/%s" % (self.slaveSpec.scheme, self.slaveSpec.host, self.slaveSpec.port, self.slaveSpec.path, path))
    
    def createJob(self, jobSpec):
        log.debug("Creating job with spec %s" % jobSpec)
        return RestApiClient.POST(self.url("/job"), postdata=jobSpec.toJson())
           
    def startJob(self, jobId):
        return RestApiClient.POST(self.url("/job/%d/start" % jobId))

    def pauseJob(self, jobId):
        return RestApiClient.POST(self.url("/job/%d/pause" % jobId))
    
    def resumeJob(self, jobId):
        return RestApiClient.POST(self.url("/job/%d/resume" % jobId))
    
    def stopJob(self, jobId):
        return RestApiClient.POST(self.url("/job/%d/stop" % jobId))
    
    def jobState(self, jobId):
        return RestApiClient.GET(self.url("/job/%d/state" % jobId))
    
    def jobResults(self, jobId, shortResults):
        if shortResults == True:
            return RestApiClient.GET(self.url("/job/%d/results?short=true" % jobId))
        else:
            return RestApiClient.GET(self.url("/job/%d/results" % jobId))
    
    def heartbeat(self):
        return RestApiClient.GET(self.url("/status/heartbeat"))

class NoSlavesAvailable(Exception):
    pass

class InsufficientSlaveCapacity(Exception):
    pass

class SlaveNotFound(Exception):
    pass

class SlaveAlreadyConnected(Exception):
    def __init__(self, slaveId=None):
        self.slaveId = slaveId

class SlaveConnectionError(Exception):
    pass

class _SlaveAllocator(object):
    def __init__(self):
        self.slaves = {}

    def _getSlaveNo(self):
        slaveNo = db.execute("SELECT slaveNo FROM slaveno").fetchone()["slaveNo"]
        db.execute("UPDATE slaveno SET slaveNo = ?", (slaveNo + 1,))
        return slaveNo

    def _getSlavesInState(self, state):
        def f((slave, status, task)):
            if status.state == state:
                return True
        result = [i for i in self.slaves.itervalues() if f(i)]
        
        if len(result) == 0:
            raise SlaveNotFound
        
        return result
    
    def _getSlaveBySlaveSpec(self, slaveSpec, asTuple=False):
        def f((slave, status, task)):
            if slave.slaveSpec == slaveSpec:
                return True
        result = [i for i in self.slaves.itervalues() if f(i)]
        # XXX
        assert len(result) <= 1
        if len(result) == 0:
            raise SlaveNotFound
        
        if asTuple:
            return result[0]
        else:
            return result[0][0]

    def _getSlaveByObject(self, slaveObj):
        def f((slave, status, task)):
            if slave == slaveObj:
                return True
        result = [i for i in self.slaves.itervalues() if f(i)]
        # XXX
        assert len(result) <= 1
        if len(result) == 0:
            raise SlaveNotFound
        
        return result[0]

    def _getSlaveById(self, slaveId, asTuple=False):
        try:
            if asTuple:
                return self.slaves[slaveId]
            else:
                return self.slaves[slaveId][0]
        except KeyError:
            raise SlaveNotFound
    
    def _getSlaveIdByObject(self, slaveObj):
        for slaveId, (slave, status, task) in self.slaves.iteritems():
            if slave == slaveObj:
                return slaveId
        raise SlaveNotFound

    def _changeSlaveState(self, slaveId, state):
        pass

    @inlineCallbacks
    def addSlave(self, slaveSpec):
        
        # try to catch a slave reconnection; else assign a new slave ID
        try:
            (connectedSlave, connectedSlaveStatus, connectedSlaveTask) = self._getSlaveBySlaveSpec(slaveSpec, asTuple=True)
            slaveId = self._getSlaveIdByObject(connectedSlave)
            log.warn("Slave %d (%s://%s:%d/%s) reconnecting.  Resetting slave state!" % (slaveId, connectedSlave.slaveSpec.scheme, connectedSlave.slaveSpec.host, connectedSlave.slaveSpec.port, connectedSlave.slaveSpec.path))    
        except SlaveNotFound:
            slaveNo = self._getSlaveNo()
        else:
            slaveNo = slaveId    
        
        slave = SlavePerspective(slaveSpec)
        status = SlaveState()
        status.state = SlaveState.CONNECTED

        # check that the slave is up and running
        request = self.checkHealth(slave)
        yield request

        if request.result != True:
            raise SlaveConnectionError
        else:
            status.state = SlaveState.IDLE
        
        # set up a heartbeat call
        task = LoopingCall(self.checkHealth, slave)
        task.start(60, now=False)
        
        self.slaves[slaveNo] = (slave, status, task)
        returnValue(slaveNo)
    
    
    @inlineCallbacks
    def checkHealth(self, slave):
        request = slave.heartbeat()
        yield request
        
        if request.result == False:
            self.degrade(slave)
            returnValue(False)
        else:
            returnValue(True)

    def degrade(self, slave):
        (slaveObj, status, task) = self._getSlaveByObject(slave)
        self._updateSlaveState(slaveObj, SlaveState.DISCONNECTED)
        task.stop()
            
    def _addChunk(self, availableSlaves, capacity):
        chunk = []
        i = 0
        for (slave, status, task) in availableSlaves:
            i += slave.slaveSpec.maxRequestsPerSec
            chunk.append((slave, status, task))
            if i >= capacity:
                break
        return chunk

    # decision rules for updating slave state.
    # in general:
    #    * if job count is 0, accept the new state.
    #    * if job count is >= 1, then "RUNNING" is the current state
    #
    # known exceptions:
    #    * slave disconnection
    def _updateSlaveState(self, slave, newState):
        (slaveObj, status, task) = self._getSlaveByObject(slave)
        
        if status.jobCount >= 1 and newState != SlaveState.DISCONNECTED:
            status.state = SlaveState.RUNNING
        else:
            status.state = newState
        
    
    @inlineCallbacks
    def allocate(self, jobSpec):
        slaves = []
        
        # check if any slaves are even connected
        if self.slaves == {}:
            log.critical("No slaves available in the system.  This is not good!")
            raise NoSlavesAvailable
        
        # this gets the maximum of the results of clientFunction(t), where t happens
        # every 20% of the job duration.  this is to get a rough idea of what the max really
        # will be, though it's really not accurate.
        clientFunction = lambda t: eval(jobSpec.clientFunction)
        maxClientsPerSec = max([clientFunction(t) for t in range(0, jobSpec.duration, int(math.ceil(.2*jobSpec.duration)))])
        
        # first try to fit the job onto idle slaves
        idleSlaves = sorted(self._getSlavesInState(SlaveState.IDLE), lambda (i, j, k), (l, m, n): i.slaveSpec.maxRequestsPerSec - l.slaveSpec.maxRequestsPerSec)
        idleCapacity = reduce(lambda x, y: x+y, [i.slaveSpec.maxRequestsPerSec for (i, j, k) in idleSlaves])
        
        # if there's more idle capacity than there are requests, then figure out
        # a subset of idle hosts to use
        if idleCapacity >= maxClientsPerSec:
            slaves += self._addChunk(idleSlaves, maxClientsPerSec)
        
        else:
            # if the job is requesting more than the total capacity of the system, then
            # just fail it.  if someone requests 1 million hits/sec, it's probably 
            # outrageous anyway.
            totalCapacity = reduce(lambda x, y: x+y, [i.slaveSpec.maxRequestsPerSec for (i, j, k) in self._getSlavesInState(SlaveState.IDLE) + self._getSlavesInState(SlaveState.ALLOCATED) + self._getSlavesInState(SlaveState.RUNNING)])
            if maxClientsPerSec > totalCapacity:
                raise InsufficientSlaveCapacity
            
            # consume all the idle hosts and if any hosts are allocated but
            # not yet used, take those
            allocatedSlaves = sorted(self._getSlavesInState(SlaveState.ALLOCATED), lambda (i, j, k), (l, m, n): i.slaveSpec.maxRequestsPerSec - l.slaveSpec.maxRequestsPerSec)
            allocatedCapacity = reduce(lambda x, y: x+y, [i.slaveSpec.maxRequestsPerSec for (i, j, k) in allocatedSlaves])

            if allocatedCapacity + idleCapacity >= maxClientsPerSec:
                slaves += self._addChunk(idleSlaves, maxClientsPerSec)
                slaves += self._addChunk(allocatedSlaves, maxClientsPerSec)


            # otherwise move in and just add more work to existing slaves            
            else:
                runningSlaves = sorted(self._getSlavesInState(SlaveState.RUNNING), lambda (i, j, k), (l, m, n): i.slaveSpec.maxRequestsPerSec - l.slaveSpec.maxRequestsPerSec)
                
                slaves += self._addChunk(idleSlaves, maxClientsPerSec)
                slaves += self._addChunk(allocatedSlaves, maxClientsPerSec)
                slaves += self._addChunk(runningSlaves, maxClientsPerSec)                
    

        # for all the slaves being allocated, do a quick health check. if one fails then
        # retry the allocation recursively and return the result
        for (slave, status, task) in slaves:
            try:
                health = yield self.checkHealth(slave)
                if health is True:
                    self._updateSlaveState(slave, SlaveState.ALLOCATED)
            except SlaveConnectionError:
                returnValue(self.allocate(jobSpec))

        returnValue([slave for (slave, status, task) in slaves])
    
    def markAsRunning(self, slave):
        (slaveObj, status, task) = self._getSlaveByObject(slave)
        status.increment()
        self._updateSlaveState(slaveObj, SlaveState.RUNNING)
    
    def markAsFinished(self, slave):
        (slaveObj, status, task) = self._getSlaveByObject(slave)
        status.decrement()        
        self._updateSlaveState(slaveObj, SlaveState.IDLE)    

SlaveAllocator = _SlaveAllocator()