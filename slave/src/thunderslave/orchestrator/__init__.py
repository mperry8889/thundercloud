from thundercloud.job import JobSpec, JobState
from ..engine import EngineFactory
import logging

log = logging.getLogger("orchestrator")

# Tracks and operates on jobs in the system, maintaining an instance
# of Engine for each job
class _Orchestrator(object):
    
    def __init__(self):
        self.jobs = {}
        self._jobSeqNo = 0
    
    def listJobs(self):
        return self.jobs.keys()

    def listJobsByState(self, state):
        jobs = self.listJobs()
        jobsInState = []
        for job in jobs:
            if self.jobs[job].state == state:
                jobsInState.append(job)
        return jobsInState

    def listActiveJobs(self):
        return self.listJobsByState(JobState.RUNNING)

    def listCompleteJobs(self):
        return self.listJobsByState(JobState.COMPLETE)        
    
    def createJob(self, jobSpec):
        self._jobSeqNo = self._jobSeqNo + 1
        # this makes things slow.
        #while self.jobs.has_key(self._jobSeqNo):
        #    self._jobSeqNo = self._jobSeqNo + 1
        
        log.debug("Creating job %s; jobspec: %s" % (self._jobSeqNo, str(jobSpec)))
        self.jobs[self._jobSeqNo] = EngineFactory.createFactory(self._jobSeqNo, jobSpec)
        return self._jobSeqNo       

    def startJob(self, jobId):
        log.debug("Starting job %d" % jobId)
        self.jobs[jobId].start()

    def pauseJob(self, jobId):
        log.debug("Pausing job %d" % jobId)
        self.jobs[jobId].pause()
    
    def resumeJob(self, jobId):
        log.debug("Resuming job %d" % jobId)
        self.jobs[jobId].resume()
    
    def stopJob(self, jobId):
        log.debug("Stopping job %d" % jobId)
        self.jobs[jobId].stop()

    def removeJob(self, jobId):
        try:
            self.jobs[jobId].stop()
        except:
            pass
        try:
            self.jobs.pop(jobId)
        except KeyError:
            pass
    
    def jobState(self, jobId):
        return self.jobs[jobId].state
    
    def jobResults(self, jobId, args):
        return self.jobs[jobId].results(args)
    
Orchestrator = _Orchestrator()