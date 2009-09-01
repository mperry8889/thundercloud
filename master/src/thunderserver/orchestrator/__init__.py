from thundercloud.slave import SlaveSpec
from thundercloud.job import JobSpec, JobState

from ..db import dbConnection as db
from perspectives import JobPerspective, SlavePerspective
from restApiClient import RestApiClient

import logging

log = logging.getLogger("orchestrator")

# Handle the multitide of jobs and slaves in the system
class _Orchestrator(object):
    def __init__(self):
        self.slaves = []
        self.jobs = {}
        
        slaveOne = SlavePerspective(None)
        slaveOne.host = "localhost"
        slaveOne.port = "8080"
        slaveOne.path = "/slave"
        slaveOne.url = "http://localhost:8080/slave"
        self.slaves.append(slaveOne)
        
    def _getJobNo(self):
        jobNo = db.execute("SELECT jobNo FROM jobno").fetchone()["jobNo"]
        db.execute("UPDATE jobno SET jobNo = ?", (jobNo + 1,))
        return jobNo
   
    def registerSlave(self, slaveSpec):
        pass
    
    def unregisterSlave(self, slaveId):
        pass
    
    def _createJobCallback(self, remoteJobId, localJobId, slave):
        print "calling back, jobid = %s/%s slave = %s" % (remoteJobId, localJobId, slave)
        self.jobs[localJobId].addSlave(slave, int(remoteJobId))
    
    def createJob(self, jobSpec):
        jobNo = self._getJobNo()
        job = JobPerspective(jobNo)
        
        # allocate a bunch of slaves here. for now we'll just use the set of
        # all slaves
        slaves = self.slaves
        
        # divide the client function to spread the load over all slaves in the set
        clientFunctionPerSlave = "(%s)/%s" % (jobSpec.clientFunction, len(slaves))
        modifiedJobSpec = JobSpec(jobSpec.toJson())
        modifiedJobSpec.clientFunction = clientFunctionPerSlave
        
        for slave in slaves:
            deferred = slave.createJob(modifiedJobSpec)
            deferred.addCallback(self._createJobCallback, jobNo, slave)

        self.jobs[jobNo] = job        
        return jobNo
    
    def startJob(self, jobId):
        self.jobs[jobId].start()
    
    def pauseJob(self, jobId):
        self.jobs[jobId].pause()
    
    def resumeJob(self, jobId):
        self.jobs[jobId].resume()
    
    def stopJob(self, jobId):
        self.jobs[jobId].stop()

    def jobState(self, jobId):
        pass
    
    def jobResults(self, jobId, args):
        pass
   
   
    def pollCallback(self, value, jobId):
        pass
    
    def poll(self, jobId):
        pass
    
    

Orchestrator = _Orchestrator()