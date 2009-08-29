from thundercloud.job import JobSpec, JobState
from ..engine import EngineFactory
from ..db import dbConnection as db

import logging

log = logging.getLogger("orchestrator")

# Tracks and operates on jobs in the system, maintaining an instance
# of Engine for each job
class _Orchestrator(object):
    
    def __init__(self):
        self.jobs = {}
    
    def _getAndUpdateJobSeqNo(self):
        jobNo = db.execute("SELECT jobNo FROM jobSeqNo").fetchone()["jobNo"]
        db.execute("UPDATE jobSeqNo SET jobNo = ?", (jobNo + 1,))
        return jobNo
    
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
        jobNo = self._getAndUpdateJobSeqNo()

        log.info("Creating job %s; jobspec: %s" % (jobNo, str(jobSpec)))
        self.jobs[jobNo] = EngineFactory.createFactory(jobNo, jobSpec)
        return jobNo

    def startJob(self, jobId):
        log.info("Starting job %d" % jobId)
        self.jobs[jobId].start()

    def pauseJob(self, jobId):
        log.info("Pausing job %d" % jobId)
        self.jobs[jobId].pause()
    
    def resumeJob(self, jobId):
        log.info("Resuming job %d" % jobId)
        self.jobs[jobId].resume()
    
    def stopJob(self, jobId):
        log.info("Stopping job %d" % jobId)
        self.jobs[jobId].stop()

    def removeJob(self, jobId):
        log.info("Removing job %s" % jobId)
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
        try:
            return self.jobs[jobId].results(args)
        except KeyError:
            try:
                dummy = EngineFactory.createFactory(jobId, { "profile": JobSpec.JobProfile._DUMMY })
                return dummy.results(args)
            except:
                return None
            
    
Orchestrator = _Orchestrator()