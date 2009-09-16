from ..db import dbConnection as db
from thundercloud.util.restApiClient import RestApiClient

from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

import logging

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


class SlaveStatus(object):
    def __init__(self):
        self.inUse = False

class SlaveAlreadyConnected(Exception):
    def __init__(self, slaveId=None):
        self.slaveId = slaveId

class _SlaveAllocator(object):
    def __init__(self):
        self.slaves = {}

    def _getSlaveNo(self):
        slaveNo = db.execute("SELECT slaveNo FROM slaveno").fetchone()["slaveNo"]
        db.execute("UPDATE slaveno SET slaveNo = ?", (slaveNo + 1,))
        return slaveNo

    @inlineCallbacks
    def addSlave(self, slaveSpec):
        for slaveId, (connectedSlave, status) in self.slaves.iteritems():
            if connectedSlave.slaveSpec.host == slaveSpec.host and \
               connectedSlave.slaveSpec.port == slaveSpec.port and \
               connectedSlave.slaveSpec.path == slaveSpec.path:
                raise SlaveAlreadyConnected(slaveId)
        
        slaveNo = self._getSlaveNo()
        slave = SlavePerspective(slaveSpec)
        status = SlaveStatus()
        self.slaves[slaveNo] = (slave, status)

        # XXX there will be some handshaking or something going on here
        
        returnValue(slaveNo)
    
    def removeSlave(self, slaveId):
        self.slaves.pop(slaveId)
    
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
        for slaveId, (slaveObj, status) in self.slaves.iteritems():
            if slaveObj == slave:
                self.removeSlave(slaveId)
                break
            
    
    @inlineCallbacks
    def allocate(self, jobSpec):
        slaves = []
        for (slave, status) in self.slaves.itervalues():
            status.inUse = True
            request = self.checkHealth(slave)
            yield request
            if request.result == True:
                slaves.append(slave)

        returnValue(slaves)

    def release(self, slaveList):
        pass
    

SlaveAllocator = _SlaveAllocator()