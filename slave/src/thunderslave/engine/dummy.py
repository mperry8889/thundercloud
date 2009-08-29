from zope.interface import Interface, Attribute, implements

from thundercloud import constants
from thundercloud.job import IJob, JobSpec, JobState, JobResults

from enginebase import IEngine
from ..db import dbConnection as db

class JobNotFound(Exception):
    pass

class DummyEngine(object):
    implements(IEngine, IJob)
  
    def __init__(self, jobId, jobSpec):

        results = db.execute("SELECT id, spec, results FROM jobs WHERE id = ?", (jobId,)).fetchone()
        if results is None:
            raise JobNotFound
        
        jobSpec = results["jobSpec"]
        jobResults = results["jobResults"]

        self.jobId = results["jobId"]
        self.requests = jobSpec.requests
        self.transferLimit = jobSpec.transferLimit
        self.duration = jobSpec.duration
        self.userAgent = jobSpec.userAgent
        self.statsInterval = jobSpec.statsInterval
        self.clientFunction = lambda t: eval(jobSpec.clientFunction)
  
        self.jobResults = jobResults
  
    # normal job operations don't work here
    def start(self):
        return
    
    def pause(self):
        return
    
    def resume(self):
        return

    def stop(self):
        return

    def state(self):
        return self.jobResults.jobState

    # generate and fill in a JobResults object
    def results(self, short=False):
        return self.jobResults