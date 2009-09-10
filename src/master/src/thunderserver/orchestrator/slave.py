from ..db import dbConnection as db
from thundercloud.util.restApiClient import RestApiClient
from twisted.internet.defer import Deferred
from twisted.internet import reactor

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


class SlaveStatus(object):
    def __init__(self):
        self.inUse = False

class SlaveAlreadyConnected(Exception):
    pass


class _SlaveAllocator(object):
    def __init__(self):
        self.slaves = {}

    def _getSlaveNo(self):
        slaveNo = db.execute("SELECT slaveNo FROM slaveno").fetchone()["slaveNo"]
        db.execute("UPDATE slaveno SET slaveNo = ?", (slaveNo + 1,))
        return slaveNo

    def addSlaveCallback(self, value, deferred):
        deferred.callback(value)
    
    def addSlaveErrback(self, value, deferred):
        deferred.errback(value)

    def addSlave(self, slaveSpec):
        deferred = Deferred()
        
        for (connectedSlave, status) in self.slaves.itervalues():
            if connectedSlave.slaveSpec.host == slaveSpec.host:
                raise SlaveAlreadyConnected
        
        slaveNo = self._getSlaveNo()
        slave = SlavePerspective(slaveSpec)
        status = SlaveStatus()
        self.slaves[slaveNo] = (slave, status)
        # XXX hack
        reactor.callLater(0.25, self.addSlaveCallback, slaveNo, deferred)
        return deferred
    
    def removeSlave(self, slaveId):
        self.slaves.pop(slaveId)
    
    def allocate(self, jobSpec):
        slaves = []
        for (slave, status) in self.slaves.itervalues():
            status.inUse = True
            slaves.append(slave)
        return slaves

    def release(self, slaveList):
        pass
    

SlaveAllocator = _SlaveAllocator()