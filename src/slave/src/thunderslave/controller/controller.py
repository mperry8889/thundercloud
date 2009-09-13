from thundercloud.spec.job import JobSpec, JobState
from ..engine import EngineFactory
from ..db import dbConnection as db

import logging
import datetime

log = logging.getLogger("controller")

class InvalidJob(Exception):
    pass

# Tracks and operates on jobs in the system, maintaining an instance
# of Engine for each job
class _Controller(object):
    
    def __init__(self):
        self.jobs = {}
    
    def _getJobNo(self):
        jobNo = db.execute("SELECT jobNo FROM jobno").fetchone()["jobNo"]
        db.execute("UPDATE jobno SET jobNo = ?", (jobNo + 1,))
        return jobNo
    
    def _kick(self, jobId):
        try:
            self.jobs.pop(jobId)
        except KeyError:
            pass
    
    def _getJob(self, jobId):
        # if job is in memory
        try:
            return self.jobs[jobId]
        # otherwise check if it's in the DB
        except KeyError:
            anonObj = type("", (), {})
            anonObj.profile = JobSpec.JobProfile.DUMMY
            dummy = EngineFactory.createFactory(jobId, anonObj)
            return dummy
        # if it's not in either then it doesn't exist
        else:
            raise InvalidJob
            
    
    def _logToDb(self, jobId, operation):
        db.execute("INSERT INTO controller (job, operation, timestamp) VALUES (?, ?, ?)", 
                    (jobId, operation, datetime.datetime.now()))        
            
    def createJob(self, jobSpec):
        jobNo = self._getJobNo()

        log.info("Creating job %s; jobspec: %s" % (jobNo, str(jobSpec)))
        self.jobs[jobNo] = EngineFactory.createFactory(jobNo, jobSpec)
        self._logToDb(jobNo, "create")
        return jobNo

    def startJob(self, jobId):
        log.info("Starting job %d" % jobId)
        self._logToDb(jobId, "start")
        self._getJob(jobId).start()

    def pauseJob(self, jobId):
        log.info("Pausing job %d" % jobId)
        self._logToDb(jobId, "pause")
        self._getJob(jobId).pause()
    
    def resumeJob(self, jobId):
        log.info("Resuming job %d" % jobId)
        self._logToDb(jobId, "resume")
        self._getJob(jobId).resume()
    
    def stopJob(self, jobId):
        log.info("Stopping job %d" % jobId)
        self._logToDb(jobId, "stop")
        self._getJob(jobId).stop()
        self._kick(jobId)

    def removeJob(self, jobId):
        log.info("Removing job %s" % jobId)
        self._logToDb(jobId, "remove")
        try:
            self._getJob(jobId).stop()
        except:
            pass
    
    def jobState(self, jobId):
        state = self._getJob(jobId).job_state
        
        # if the job is done, kick the engine out from memory
        if state == JobState.COMPLETE:
            self._kick(jobId)
            
        return state
    
    def jobResults(self, jobId, short):
        results = self._getJob(jobId).results(short)
        
        if results.job_state == JobState.COMPLETE:
            self._kick(jobId)
        
        return results