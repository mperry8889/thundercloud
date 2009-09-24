from Queue import Queue
from zope.interface import Interface, Attribute, implements
import time
import math
import logging
import datetime
import copy

from twisted.web.client import HTTPDownloader, _parse
from twisted.internet import reactor

from thundercloud import constants
from thundercloud.spec.job import IJob, JobState, JobResults

from ..db import dbConnection as db

log = logging.getLogger("engine")

# This is our custom HTTP client factory.  Note that it's an old-style class.
class StatisticalHTTPDownloader(HTTPDownloader):        
    def __init__(self, url, fileOrName, method="GET", postdata=None, cookies={}, headers=None, agent=None, timeout=None):
        # XXX re-add support for cookies and timeout to HTTPDownloader call
        HTTPDownloader.__init__(self, url, fileOrName, method=method, postdata=postdata, headers=headers, agent=agent)
        self.value = {
            "startTime": time.time(),
            "timeToConnect": 0,
            "timeToFirstByte": 0,
            "elapsedTime": 0,
            "bytesTransferred": 0,
        }
        self.cookies = cookies
        self.timeout = timeout
    
    def buildProtocol(self, addr):
        self.value["timeToConnect"] = time.time() - self.value["startTime"]
        return HTTPDownloader.buildProtocol(self, addr)
        
    def pageStart(self, partialContent):
        self.value["timeToFirstByte"] = time.time() - self.value["startTime"]
        return HTTPDownloader.pageStart(self, partialContent)
        
    def pagePart(self, data):
        self.value["bytesTransferred"] += len(data)
        return HTTPDownloader.pagePart(self, data)
            
    def pageEnd(self):
        self.value["elapsedTime"] = time.time() - self.value["startTime"]
        return HTTPDownloader.pageEnd(self)



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
        self.userAgent = str("thundercloud client/%s" % constants.VERSION)
        self.iterator = lambda: True
        self.httpClientRequestQueue = Queue()
        self.jobState = JobState.NEW
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
        self.errors = copy.deepcopy(JobResults().results_errors)
        self.statisticsByTime = copy.deepcopy(JobResults().results_byTime)
        self._averageTimeToConnect = 0
        self._averageTimeToFirstByte = 0
        self._averageResponseTime = 0
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
                                             str(self.requests[url]["method"]), 
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
        if self.jobState != JobState.NEW:
            return
        
        log.debug("Starting job %d" % self.jobId)
        
        self.startTime = time.time()
        self.jobState = JobState.RUNNING
        self.iterator()


    # handy method to set up a Deferred and set up callbacks.  this needs to be
    # a separate method so it can easily be triggered by reactor.callLater
    def _request(self, host, port, method, url, postdata, cookies):
        factory = StatisticalHTTPDownloader(url,
                                            "/dev/null",
                                            method=method,
                                            postdata=postdata,
                                            cookies=cookies, 
                                            agent=str(self.userAgent),
                                            timeout=self.timeout)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback)
        factory.deferred.addErrback(self.errback)
        try:
            self.bytesTransferred = self.bytesTransferred + len(cookies)
            self.bytesTransferred = self.bytesTransferred + len(postdata)
        except TypeError:
            pass
        

    # mark a job as paused.  derived class' iteration loops should be
    # careful to check the job's state before continuing, making pause/resume
    # very simple
    def pause(self):
        if self.jobState != JobState.RUNNING:
            raise Exception, "Not running"
        
        self.jobState = JobState.PAUSED
        self._timeAtPause = time.time()
        
        log.debug("Pausing job %d" % self.jobId)
    
    
    # mark the job as running, and spin up new clients
    def resume(self):
        # only resume paused jobs
        if self.jobState != JobState.PAUSED:
            raise Exception, "Not paused"
        
        self.pausedTime = self.pausedTime + (time.time() - self._timeAtPause)
        self.jobState = JobState.RUNNING
        self.iterator()
        
        log.debug("Resuming job %d" % self.jobId)
    
    
    # stop the job and mark it as complete
    def stop(self):
        if self.jobState == JobState.COMPLETE:
            return
                
        self.jobState = JobState.COMPLETE
        self.endTime = time.time()
        self._generateStats(force=True)
        
        db.execute("UPDATE jobs SET endTime = ? WHERE id = ?", (datetime.datetime.now(), self.jobId))
        db.execute("UPDATE jobs SET results = ? WHERE id = ?", (self.results(), self.jobId))    
        log.debug("Job %d complete" % self.jobId)
    
    
    # some bookkeeping
    def _bookkeep(self, value):
        self.iterations = self.iterations + 1
        self.bytesTransferred = self.bytesTransferred + value["bytesTransferred"]
        self.elapsedTime = time.time() - self.startTime - self.pausedTime
        self._averageTimeToConnect = (value["timeToConnect"] + ((self.iterations-1) * self._averageTimeToConnect))/self.iterations
        self._averageTimeToFirstByte = (value["timeToFirstByte"] + ((self.iterations-1) * self._averageTimeToFirstByte))/self.iterations
        self._averageResponseTime = (value["elapsedTime"] + ((self.iterations-1) * self._averageResponseTime))/self.iterations
    
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
                    "iterations_total": self.iterations,
                    "iterations_success": self.requestsCompleted,
                    "iterations_fail": self.requestsFailed,
                    "timeToConnect": self._averageTimeToConnect,
                    "timeToFirstByte": self._averageTimeToFirstByte,
                    "responseTime": self._averageResponseTime,
                    "requestsPerSec": float(self.iterations - self.statisticsByTime[self._statsBookmark]["iterations_total"])/float(self.elapsedTime - self._statsBookmark),
                    "throughput": float(self.bytesTransferred - self.statisticsByTime[self._statsBookmark]["bytesTransferred"])/float(self.elapsedTime - self._statsBookmark),
                    "errors": self.errors,
                    "bytesTransferred": self.bytesTransferred,
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
    def callback(self, value):
        self._bookkeep(value)
        self._generateStats()
        self.requestsCompleted = self.requestsCompleted + 1

    
    # default errback -- see comments for callback()
    def errback(self, value):
        log.debug("Firing errback.  Error: %s" % value)
        self._bookkeep("")
        self._generateStats()
        self.requestsFailed = self.requestsFailed + 1
        
        # this is probably going to slow things down in a super high traffic environment
        # due to string searches, but there doesn't seem to be a better way.  errback 
        # handling is not very awesome, especially in terms of propagating exceptions
        if "Connection lost" in value.getErrorMessage():
            self.errors["connectionLost"] = self.errors["connectionLost"] + 1
        elif "TimeoutError" in value.getErrorMessage():
            self.errors["timeout"] = self.errors["timeout"] + 1
        elif "ConnectBindError" in value.getErrorMessage():
            self.errors["unknown"] = self.errors["unknown"] + 1 
        else:
            self.errors["unknown"] = self.errors["unknown"] + 1


    # return the job's state
    def state(self):
        return self.jobState

    # generate and fill in a JobResults object
    def results(self, short=False):        
        jobResults = JobResults()
        jobResults.job_id = self.jobId
        jobResults.job_state = self.jobState
        jobResults.job_nodes = 1
        jobResults.iterations_total = self.iterations
        jobResults.iterations_success = self.requestsCompleted
        jobResults.iterations_fail = self.requestsFailed
        jobResults.limits_transfer = self.transferLimit
        jobResults.limits_duration = self.duration
        jobResults.time_elapsed = self.elapsedTime
        jobResults.time_paused = self.pausedTime
        jobResults.transfer_total = self.bytesTransferred
        jobResults.results_errors = copy.deepcopy(self.errors)      

        # don't attach statistics if the caller is looking for short results
        if short == True:
            try:
                del(jobResults.results_byTime)
            except AttributeError:
                pass
        else:
            jobResults.results_byTime = copy.deepcopy(self.statisticsByTime)
        
        return jobResults
    