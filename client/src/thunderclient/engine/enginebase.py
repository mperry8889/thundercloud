from Queue import Queue
from zope.interface import Interface, Attribute, implements
import time
import math

from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

from thundercloud import constants
from ..orchestrator.job import IJob
from ..orchestrator.job import JobSpec, JobState, JobResults

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
    clientFunction = lambda self, t: ((10*math.sin(.1*t))+10)
    requests = {"http://unshift.net":{}}
    userAgent = "thundercloud client/%s" % constants.VERSION
    iterator = lambda: True
    httpClientRequestQueue = Queue()
    state = JobState.NEW
        
    # attributes for time management
    duration = 60
    starTime = None
    endTime = None
    elapsedTime = 0.00000001    # so clientFunction(0) != 0
    
    # attributes for data management
    bytesTransferred = 0
    transferLimit = float("inf")
    
    # attributes for statistics generation    
    iterations = 0
    statisticsByTime = {}
    statsGranularity = 10
    _statsBookmark = 0          # shortcut to last time stats were generated.
                                # avoids listing/sorting statisticsByTime keys
    
  
    def __init__(self, jobSpec):
        # dump the host/port/URLs to be fetched into a queue
        for url in self.requests.keys():
            scheme, host, port, path = _parse(url)
            self.httpClientRequestQueue.put([host, port, url])

        self.statisticsByTime[0] = {
            "iterations": 0,
            "clientsPerSec": 0,
            "clients": 0,
        }
  
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
    def _request(self, host, port, url):
        requestTime = time.time()
        factory = HTTPClientFactory(url, agent=self.userAgent)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback, requestTime)
        factory.deferred.addErrback(self.errback, requestTime)


    # mark a job as paused.  derived class' iteration loops should be
    # careful to check the job's state before continuing, making pause/resume
    # very simple
    def pause(self):
        self.state = JobState.PAUSED
    
    
    # mark the job as running, and spin up new clients
    def resume(self):
        # only resume paused jobs
        if self.state != JobState.PAUSED:
            raise Exception, "Not paused"
        
        self.state = JobState.RUNNING
        self.iterator()
    
    
    # stop the job and mark it as complete
    def stop(self):
        if self.state == JobState.COMPLETE:
            return
        
        self.endTime = time.time()
        self.state = JobState.COMPLETE
        self.dump()
    
    
    # some bookkeeping
    def _bookkeeping(self, value, requestTime):
        self.iterations = self.iterations + 1
        self.bytesTransferred = self.bytesTransferred + len(value)
        self.elapsedTime = time.time() - self.startTime
    
        if self.elapsedTime >= self.duration:
            self.stop()
    
        if self.bytesTransferred >= self.transferLimit:
            self.stop()        
    
    # default callback which handles bookkeeping.  derived classes
    # can re-implement callback() but should probably call this method
    # via super(), or else duplicate the bookkeeping code
    def callback(self, value, requestTime):        
        self._bookkeeping(value, requestTime)
        
        # if it's been 1 or more seconds since the last time we took stats
        # (avg TuT, number of concurrent requests) then let's do it again
        if int(self.elapsedTime - self._statsBookmark) >= self.statsGranularity:
            try:
                self.statisticsByTime[self.elapsedTime] = {
                    "iterations": self.iterations,
                    "clientsPerSec": float(self.iterations - self.statisticsByTime[self._statsBookmark]["iterations"])/float(self.elapsedTime - self._statsBookmark),
                    # XXX: this isn't entirely accurate. this gives f(t) but isn't the
                    # actual number of clients in the system
                    "clients": abs(int(math.ceil(self.clientFunction(time.time())))),
                }
                self._statsBookmark = self.elapsedTime
            except ZeroDivisionError:
                pass
                
    
    # default errback -- see comments for callback()
    def errback(self, value, requestTime):
        print value
        self._bookkeeping("", requestTime)


    # dump job information to the console.  useful for debugging.
    def dump(self):
        print "state: %s" % self.state
        print "start time: %s, end time: %s, elapsed time: %s" % (self.startTime, self.endTime, self.elapsedTime)
        print "bytes transferred: %s" % self.bytesTransferred
        print "iterations: %s" % self.iterations
        print "stats last: %s" % self.statisticsByTime[sorted(self.statisticsByTime.keys())[-1]]
        print "stats total:"
        for key in sorted(self.statisticsByTime.keys()):
            print "t=%s" % int(key)
            print self.statisticsByTime[key]
            