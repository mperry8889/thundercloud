from zope.interface import implements

from thundercloud.spec.job import IJob

from base import IEngine
from ..db import dbConnection as db

import copy

class JobNotFound(Exception):
    pass

class JobHasNoResults(Exception):
    pass

class DummyEngine(object):
    implements(IEngine, IJob)
  
    def __init__(self, jobId, jobSpec):       
        results = db.execute("SELECT id, spec, results FROM jobs WHERE id = ?", (jobId,)).fetchone()   
        if results is None:
            raise JobNotFound
        if results["results"] is None:
            raise JobHasNoResults
        
        self.jobSpec = results["spec"]
        self.jobResults = results["results"]

        self.jobId = results["id"]
        self.requests = self.jobSpec.requests
        self.transferLimit = self.jobSpec.transferLimit
        self.duration = self.jobSpec.duration
        self.userAgent = self.jobSpec.userAgent
        self.statsInterval = self.jobSpec.statsInterval
        self.clientFunction = self.jobSpec.clientFunction
        
        
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
        return self.jobResults.job_state

    # generate and fill in a JobResults object
    def results(self, short=False):
        if short == True:
            results = self.jobResults
            try:
                del(results.results_byTime)
            except AttributeError:
                pass
            return results
        
        return self.jobResults