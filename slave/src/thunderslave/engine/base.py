from Queue import Queue
from zope.interface import Interface, Attribute, implements
import time
import math
import logging
import datetime

from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

from thundercloud import constants
from thundercloud.job import IJob, JobState, JobResults

from ..db import dbConnection as db

log = logging.getLogger("engine")

class IEngine(Interface):
    clients = Attribute("""(Theoretical) clients in the system""")
    
    def results(self):
        """Generate a JobResult object"""

# This class sets up the guidelines for how engines should work -- mostly
# in terms of statistics gathering and ensuring basic functionality is 
# consistent across implementations, and taking care of some muckwork that
# doesn't need to be reproduced
class EngineBase(object):
    implements(IEngine, IJob)
  
    def __init__(self, jobId, jobSpec):
        self.jobId = jobId
        self.jobSpec = jobSpec
        
        # attributes which configure the engine
        self.clientFunction = lambda self, t: 1
        self.requests = {"":{}}
        self.userAgent = "thundercloud client/%s" % constants.VERSION
        self.iterator = lambda: True
        self.httpClientRequestQueue = Queue()
        self.state = JobState.NEW
        self.timeout = 10
    
        # attributes for time management
        self.duration = float("inf") #60
        self.startTime = None
        self.endTime = None
        self.elapsedTime = 0.00000001    # so clientFunction(0) != 0
        self.pausedTime = 0.0
        self._timeAtPause = 0.0
        
        # attributes for data management
        self.bytesTransferred = 0
        self.transferLimit = float("inf")
        
        # attributes for statistics generation    
        self.iterations = 0
        self.requestsCompleted = 0
        self.requestsFailed = 0
        self.errors = {
            "connectionLost": 0,
            "serviceNotAvailable": 0,
            "unknown": 0,
            "timeout": 0,     
        }
        self._averageResponseTime = 0
        self.statisticsByTime = {
            0: {
                "iterations": 0,
                "requestsCompleted": 0,
                "requestsFailed": 0,
                "requestsPerSec": 0,
                "clients": 0,
                "averageResponseTime": 0,
            }
        }
        self.statsInterval = 60
        self._statsBookmark = 0          # shortcut to last time stats were generated.
                                         # avoids listing/sorting statisticsByTime keys
        
        # read the job spec and update attributes
        self.requests = jobSpec.requests
        self.transferLimit = jobSpec.transferLimit
        self.duration = jobSpec.duration
        self.userAgent = jobSpec.userAgent
        self.statsInterval = jobSpec.statsInterval
        self.timeout = jobSpec.timeout
        self.clientFunction = lambda t: eval(jobSpec.clientFunction)
        
        # dump the host/port/URLs to be fetched into a queue
        for url in self.requests.keys():
            scheme, host, port, path = _parse(str(url))
            self.httpClientRequestQueue.put([host, port, 
                                             self.requests[url]["method"], 
                                             str(url), 
                                             self.requests[url]["postdata"],
                                             self.requests[url]["cookies"]])
        
        db.execute("INSERT INTO jobs (id, startTime, spec) VALUES (?, ?, ?)", 
                    (self.jobId, datetime.datetime.now(), self.jobSpec))
        db.execute("INSERT INTO accounting (job, elapsedTime, bytesTransferred) VALUES (?, ?, ?)", 
                    (self.jobId, 0, 0))

  
    # start the engine.  set the current time and set the job state as running,
    # then spin up all of the clients
    def start(self):
        # only start once
        if self.state != JobState.NEW:
            return
        
        log.debug("Starting job %d" % self.jobId)
        
        self.startTime = time.time()
        self.state = JobState.RUNNING
        self.iterator()


    # handy method to set up a Deferred and set up callbacks.  this needs to be
    # a separate method so it can easily be triggered by reactor.callLater
    def _request(self, host, port, method, url, postdata, cookies):
        requestTime = time.time()
        factory = HTTPClientFactory(url,
                                    method=method,
                                    postdata=postdata,
                                    cookies=cookies, 
                                    agent=self.userAgent,
                                    timeout=self.timeout)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback, requestTime)
        factory.deferred.addErrback(self.errback, requestTime)
        try:
            self.bytesTransferred = self.bytesTransferred + len(cookies)
            self.bytesTransferred = self.bytesTransferred + len(postdata)
        except TypeError:
            pass
        

    # mark a job as paused.  derived class' iteration loops should be
    # careful to check the job's state before continuing, making pause/resume
    # very simple
    def pause(self):
        if self.state != JobState.RUNNING:
            raise Exception, "Not running"
        
        self.state = JobState.PAUSED
        self._timeAtPause = time.time()
        
        log.debug("Pausing job %d" % self.jobId)
    
    
    # mark the job as running, and spin up new clients
    def resume(self):
        # only resume paused jobs
        if self.state != JobState.PAUSED:
            raise Exception, "Not paused"
        
        self.pausedTime = self.pausedTime + (time.time() - self._timeAtPause)
        self.state = JobState.RUNNING
        self.iterator()
        
        log.debug("Resuming job %d" % self.jobId)
    
    
    # stop the job and mark it as complete
    def stop(self):
        if self.state == JobState.COMPLETE:
            return
                
        self.state = JobState.COMPLETE
        self.endTime = time.time()
        self._generateStats(force=True)
        
        db.execute("UPDATE jobs SET endTime = ? WHERE id = ?", (datetime.datetime.now(), self.jobId))
        db.execute("UPDATE jobs SET results = ? WHERE id = ?", (self.results(), self.jobId))    
        log.debug("Job %d complete" % self.jobId)
    
    
    # some bookkeeping
    def _bookkeep(self, value, requestTime):
        self.iterations = self.iterations + 1
        self.bytesTransferred = self.bytesTransferred + len(value)
        self.elapsedTime = time.time() - self.startTime - self.pausedTime
        self._averageResponseTime = ((time.time() - requestTime) + ((self.iterations-1) * self._averageResponseTime))/self.iterations
    
        if self.elapsedTime >= self.duration:
            self.stop()
    
        if self.bytesTransferred >= self.transferLimit:
            self.stop()        
    
    
    # generate statistics
    def _generateStats(self, force=False):
        # if another timeslice has passed since the last time we took stats
        # (requests/sec, number of concurrent requests) then let's do it again.
        if (self.elapsedTime - self._statsBookmark >= self.statsInterval) or force:
            try:
                self.statisticsByTime[self.elapsedTime] = {
                    "iterations": self.iterations,
                    "requestsCompleted": self.requestsCompleted,
                    "requestsFailed": self.requestsFailed,
                    "requestsPerSec": float(self.iterations - self.statisticsByTime[self._statsBookmark]["iterations"])/float(self.elapsedTime - self._statsBookmark),
                    # XXX: this isn't entirely accurate. this gives f(t) but isn't the
                    # actual number of clients in the system
                    "clients": min(constants.CLIENT_UPPER_BOUND, abs(int(math.ceil(self.clientFunction(time.time()))))),
                    "averageResponseTime": self._averageResponseTime,
                }
                
                # if it's been less than 1 second since the last stats
                # calculation, the results can get skewed.  for example
                # if the engine is humming along at 15 requests/sec and 
                # we get stats at time t and t+0.001 during which there have
                # been 2 hits, the calculation will say there has been 
                # 2/.001 = 2000 hits/sec.  so in this case, just steal it
                # from time t, i guess
                if self.elapsedTime - self._statsBookmark < 1.0:
                    self.statisticsByTime[self.elapsedTime]["requestsPerSec"] = self.statisticsByTime[self._statsBookmark]["requestsPerSec"]
               
                
                db.execute("UPDATE accounting SET elapsedTime = ?, bytesTransferred = ? WHERE job = ?", 
                              (self.elapsedTime, self.bytesTransferred, self.jobId))
                
                self._statsBookmark = self.elapsedTime
            except ZeroDivisionError:
                pass
    
    
    # default callback which handles bookkeeping.  derived classes
    # can re-implement callback() but should probably call this method
    # via super(), or else duplicate the bookkeeping code
    def callback(self, value, requestTime):
        self._bookkeep(value, requestTime)
        self._generateStats()
        self.requestsCompleted = self.requestsCompleted + 1

    
    # default errback -- see comments for callback()
    def errback(self, value, requestTime):
        self._bookkeep("", requestTime)
        self._generateStats()
        self.requestsFailed = self.requestsFailed + 1
        
        # this is probably going to slow things down in a super high traffic environment
        # due to string searches, but there doesn't seem to be a better way.  errback 
        # handling is not very awesome, especially in terms of propagating exceptions
        if "Connection lost" in value.getErrorMessage():
            self.errors["connectionLost"] = self.errors["connectionLost"] + 1
        elif "TimeoutError" in value.getErrorMessage():
            self.errors["timeout"] = self.errors["timeout"] + 1
        else:
            self.errors["unknown"] = self.errors["unknown"] + 1


    # generate and fill in a JobResults object
    def results(self, short=False):
        jobResults = JobResults()
        jobResults.jobId = self.jobId
        jobResults.state = self.state
        jobResults.iterations = self.iterations
        jobResults.transferLimit = self.transferLimit
        jobResults.bytesTransferred = self.bytesTransferred
        jobResults.duration = self.duration
        jobResults.elapsedTime = self.elapsedTime
        jobResults.errors = self.errors
        jobResults.requestsCompleted = self.requestsCompleted
        jobResults.requestsFailed = self.requestsFailed
        
        # don't attach statistics if the caller is looking for short results
        if short == True:
            try:
                del(jobResults.statisticsByTime)
            except AttributeError:
                pass
        else:
            jobResults.statisticsByTime = self.statisticsByTime
        
        return jobResults
    