from ..db import dbConnection as db
from restApiClient import RestApiClient

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


class _SlaveAllocator(object):
    def __init__(self):
        self.slaves = {}

    def addSlave(self, slaveSpec):
        slave = SlavePerspective(slaveSpec)
        self.slaves[slave] = SlaveStatus()
    
    def removeSlave(self, slave):
        self.slaves.pop(slave)
    
    def getSlaveByHost(self, host):
        for slave in self.slaves:
            if slave.host == host:
                return slave
    
    def recommend(self, jobSpec):
        return self.slaves.keys()
    
    def allocate(self, allocation):
        for slave in allocation:
            self.slaves[slave].inUse = True

    def release(self, allocation):
        for slave in allocation:
            self.slaves[slave].inUse = False
    

    

SlaveAllocator = _SlaveAllocator()