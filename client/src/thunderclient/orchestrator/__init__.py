from ..engine import EngineFactory

class JobSpec(object):
    pass

class Job(object):
    class State(object):
        NEW = 0
        RUNNING = 1
        PAUSED = 2
        COMPLETE = 3

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
        
        self.__jobs[jobNo] = EngineFactory.createFactory()      
        return jobNo
        

    def startJob(self, jobId):
        self.__jobs[jobId].start()

    def pauseJob(self, jobId):
        pass
    
    def resumeJob(self, jobId):
        pass
    
    def stopJob(self, jobId):
        self.__jobs[jobId].stop()

    def removeJob(self, jobId):
        pass

    def jobStatus(self, jobId):
        pass
    
Orchestrator = _Orchestrator()