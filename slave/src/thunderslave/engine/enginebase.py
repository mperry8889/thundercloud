from Queue import Queue
from zope.interface import Interface, Attribute, implements
import time
import math

from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

from thundercloud import constants
from thundercloud.job import IJob, JobSpec, JobState, JobResults

class IEngine(Interface):
    clients = Attribute("""foo""")
    
    def results(self):
        """Generate a JobResult object"""

# This class sets up the guidelines for how engines should work -- mostly
# in terms of statistics gathering and ensuring basic functionality is 
# consistent across implementations, and taking care of some muckwork that
# doesn't need to be reproduced
class EngineBase(object):
    implements(IEngine, IJob)

    # attributes which configure the engine
    clientFunction = lambda self, t: 1
    requests = {"":{}}
    userAgent = "thundercloud client/%s" % constants.VERSION
    iterator = lambda: True
    httpClientRequestQueue = Queue()
    state = JobState.NEW

    # attributes for time management
    duration = float("inf") #60
    startTime = None
    endTime = None
    elapsedTime = 0.00000001    # so clientFunction(0) != 0
    pausedTime = 0.0
    _timeAtPause = 0.0
    
    # attributes for data management
    bytesTransferred = 0
    transferLimit = float("inf")
    
    # attributes for statistics generation    
    iterations = 0
    errors = {
        "connectionLost": 0,
        "serviceNotAvailable": 0,
        "unknown": 0,      
    }
    statisticsByTime = {
        0: {
            "iterations": 0,
            "requestsPerSec": 0,
            "clients": 0,            
        }
    }
    statsGranularity = 60
    _statsBookmark = 0          # shortcut to last time stats were generated.
                                # avoids listing/sorting statisticsByTime keys
    
  
    def __init__(self, jobSpec):
        self.requests = jobSpec.requests
        self.transferLimit = jobSpec.transferLimit
        self.duration = jobSpec.duration
        self.userAgent = jobSpec.userAgent
        self.statsGranularity = jobSpec.statsGranularity
        self.clientFunction = lambda t: eval(jobSpec.clientFunction)
        
        # dump the host/port/URLs to be fetched into a queue
        for url in self.requests.keys():
            scheme, host, port, path = _parse(url)
            self.httpClientRequestQueue.put([host, port, 
                                             self.requests[url]["method"], 
                                             url, 
                                             self.requests[url]["postdata"],
                                             self.requests[url]["cookies"]])

  
    # start the engine.  set the current time and set the job state as running,
    # then spin up all of the clients
    def start(self):
        # only start once
        if self.state != JobState.NEW:
            raise Exception, "Job not new"
        
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
                                    agent=self.userAgent)
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
    
    
    # mark the job as running, and spin up new clients
    def resume(self):
        # only resume paused jobs
        if self.state != JobState.PAUSED:
            raise Exception, "Not paused"
        
        self.pausedTime = self.pausedTime + (time.time() - self._timeAtPause)
        self.state = JobState.RUNNING
        self.iterator()
    
    
    # stop the job and mark it as complete
    def stop(self):
        if self.state == JobState.COMPLETE:
            return
        
        self.state = JobState.COMPLETE
        self.endTime = time.time()
        self._generateStats(force=True)
    
    
    # some bookkeeping
    def _bookkeep(self, value, requestTime):
        self.iterations = self.iterations + 1
        self.bytesTransferred = self.bytesTransferred + len(value)
        self.elapsedTime = time.time() - self.startTime - self.pausedTime
    
        if self.elapsedTime >= self.duration:
            self.stop()
    
        if self.bytesTransferred >= self.transferLimit:
            self.stop()        
    
    
    # generate statistics
    def _generateStats(self, force=False):
        # if another timeslice has passed since the last time we took stats
        # (requests/sec, number of concurrent requests) then let's do it again.
        if (self.elapsedTime - self._statsBookmark >= self.statsGranularity) or force:
            try:
                self.statisticsByTime[self.elapsedTime] = {
                    "iterations": self.iterations,
                    "requestsPerSec": float(self.iterations - self.statisticsByTime[self._statsBookmark]["iterations"])/float(self.elapsedTime - self._statsBookmark),
                    # XXX: this isn't entirely accurate. this gives f(t) but isn't the
                    # actual number of clients in the system
                    "clients": min(constants.CLIENT_UPPER_BOUND, abs(int(math.ceil(self.clientFunction(time.time()))))),
                }
                self._statsBookmark = self.elapsedTime
            except ZeroDivisionError:
                pass
    
    
    # default callback which handles bookkeeping.  derived classes
    # can re-implement callback() but should probably call this method
    # via super(), or else duplicate the bookkeeping code
    def callback(self, value, requestTime):
        self._bookkeep(value, requestTime)
        self._generateStats()

    
    # default errback -- see comments for callback()
    def errback(self, value, requestTime):
        self._bookkeep("", requestTime)
        self._generateStats()
        
        # this is probably going to slow things down in a super high traffic environment
        # due to string searches, but there doesn't seem to be a better way.  errback 
        # handling is not very awesome, especially in terms of propagating exceptions
        if "Connection lost" in value.getErrorMessage():
            self.errors["connectionLost"] = self.errors["connectionLost"] + 1


    # generate and fill in a JobResults object
    def results(self):
        jobResults = JobResults()
        jobResults.iterations = self.iterations
        jobResults.bytesTransferred = self.bytesTransferred
        jobResults.elapsedTime = self.elapsedTime
        jobResults.statisticsByTime = self.statisticsByTime
        jobResults.errors = self.errors
        return jobResults


    # dump job information to the console.  useful for debugging.
    def dump(self):
        print "state: %s" % self.state
        print "start time: %s, end time: %s, elapsed time: %s" % (self.startTime, self.endTime, self.elapsedTime)
        print "bytes transferred: %s" % self.bytesTransferred
        print "iterations: %s" % self.iterations
        print "elapsed time: %s" % self.elapsedTime
        print "paused time: %s" % self.pausedTime
        print "stats last: %s" % self.statisticsByTime[sorted(self.statisticsByTime.keys())[-1]]
        print "stats total:"
        for key in sorted(self.statisticsByTime.keys()):
            print "t=%s" % key
            print self.statisticsByTime[key]
        print "errors:"
        print self.errors