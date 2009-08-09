from job import Job
from job import JobSpec
from ..engine import EngineFactory

# Tracks and operates on jobs in the system, maintaining an instance
# of Engine for each job
class _Orchestrator(object):
    __jobs = {}
    __jobSeqNo = 0
    
    def __init__(self):
        pass
    
    def listJobs(self):
        return self.__jobs.keys()
    
    def createJob(self, jobSpec, start=False):
        jobNo = self.__jobSeqNo
        self.__jobSeqNo = self.__jobSeqNo + 1
        
        self.__jobs[jobNo] = EngineFactory.createFactory(jobSpec)      
        return jobNo       

    def startJob(self, jobId):
        self.__jobs[jobId].start()

    def pauseJob(self, jobId):
        self.__jobs[jobId].pause()
    
    def resumeJob(self, jobId):
        self.__jobs[jobId].resume()
    
    def stopJob(self, jobId):
        self.__jobs[jobId].stop()

    def removeJob(self, jobId):
        try:
            self.__jobs[jobId].stop()
        except:
            pass
        try:
            self.__jobs.pop(jobId)
        except KeyError:
            pass
    
    def jobState(self, jobId):
        return self.__jobs[jobId].state()
    
Orchestrator = _Orchestrator()