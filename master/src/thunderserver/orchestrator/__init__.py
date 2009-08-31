from thundercloud.slave import SlaveSpec
from thundercloud.job import JobSpec, JobState
from ..db import dbConnection as db

import logging

log = logging.getLogger("orchestrator")


class _Orchestrator(object):
    def __init__(self):
        self.slaves = []
        self.jobs = []
    
    def registerSlave(self, slaveSpec):
        pass
    
    def unregisterSlave(self, slaveId):
        pass
    
    def createJob(self, jobSpec):
        pass
    
    def startJob(self, jobId):
        pass
    
    def pauseJob(self, jobId):
        pass
    
    def resumeJob(self, jobId):
        pass
    
    def stopJob(self, jobId):
        pass
    
    

Orchestrator = _Orchestrator()