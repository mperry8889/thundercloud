from thundercloud.slave import SlaveSpec
from thundercloud.job import JobSpec, JobState

from twisted.internet.defer import Deferred, DeferredList

from ..db import dbConnection as db
from perspectives import JobPerspective, SlavePerspective
from restApiClient import RestApiClient

import simplejson as json

import logging
import datetime

log = logging.getLogger("orchestrator")

# Handle the multitide of jobs and slaves in the system
class _Orchestrator(object):
    def __init__(self):
        self.slaves = []
        self.jobs = {}
 
        _slaves = ["192.168.1.151","192.168.1.152","192.168.1.153"]

        for i in _slaves:
            slaveSpec = SlaveSpec()
            slaveSpec.host = i
            slaveSpec.port = "7000"
            slaveSpec.path = "/"
            self.slaves.append(slaveSpec)
        
    def _getJobNo(self):
        jobNo = db.execute("SELECT jobNo FROM jobno").fetchone()["jobNo"]
        db.execute("UPDATE jobno SET jobNo = ?", (jobNo + 1,))
        return jobNo

    def _logToDb(self, jobId, operation):
        db.execute("INSERT INTO orchestrator (job, operation, timestamp) VALUES (?, ?, ?)", 
                    (jobId, operation, datetime.datetime.now()))  

    def registerSlave(self, slaveSpec):
        pass
    
    def unregisterSlave(self, slaveId):
        pass

    # create a job perspective object locally, and create a job on
    # all remote servers.
    
    def createJobSlaveCallback(self, result, slave):
        return result, slave
    
    def createJobCallback(self, results, jobId, deferred):
        for (success, result) in results:
            if success == True:
                (remoteJobId, slave) = result
                remoteJobId = int(json.loads(remoteJobId))
                self.jobs[jobId].addSlave(slave, remoteJobId)
            else:
                deferred.errback(jobId)
                break
            
        self._logToDb(jobId, "create")
        deferred.callback(jobId)
    
    def createJob(self, jobSpec):
        jobNo = self._getJobNo()
        job = JobPerspective(jobNo, jobSpec)
        self.jobs[jobNo] = job
        deferred = Deferred()
        
        # allocate a bunch of slaves here. for now we'll just use the set of
        # all slaves
        slaves = self.slaves
        
        # divide the client function to spread the load over all slaves in the set
        clientFunctionPerSlave = "(%s)/%s" % (jobSpec.clientFunction, len(slaves))
        modifiedJobSpec = JobSpec(jobSpec.toJson())
        modifiedJobSpec.clientFunction = clientFunctionPerSlave
        
        slaveRequests = []
        for slave in slaves:
            request = slave.createJob(modifiedJobSpec)
            request.addCallback(self.createJobSlaveCallback, slave)
            slaveRequests.append(request)
        
        deferredList = DeferredList(slaveRequests)
        deferredList.addCallback(self.createJobCallback, jobNo, deferred)
        
        return deferred
    
    
    def startJob(self, jobId):
        self._logToDb(jobId, "start")
        return self.jobs[jobId].start()
    
    def pauseJob(self, jobId):
        self._logToDb(jobId, "pause")
        return self.jobs[jobId].pause()
    
    def resumeJob(self, jobId):
        self._logToDb(jobId, "resume")
        return self.jobs[jobId].resume()
    
    def stopJob(self, jobId):
        self._logToDb(jobId, "stop")
        return self.jobs[jobId].stop()

    def jobState(self, jobId):
        return self.jobs[jobId].state()
    
    def jobResults(self, jobId, short):
        return self.jobs[jobId].results(short)
