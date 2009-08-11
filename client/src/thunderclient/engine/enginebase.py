from Queue import Queue
from zope.interface import Interface, Attribute, implements
import time

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
    clientFunction = lambda self, t: 20
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
    
    # attributes for statistics generation    
    iterations = 0
    errors = 0
    
  
    def __init__(self, jobSpec):
        # dump the host/port/URLs to be fetched into a queue
        for url in self.requests.keys():
            scheme, host, port, path = _parse(url)
            self.httpClientRequestQueue.put([host, port, url])
  
    # start the engine.  set the current time and set the job state as running,
    # then spin up all of the clients
    def start(self):
        # only start once
        if self.state != JobState.NEW:
            raise Exception, "Job not new"
        
        self.startTime = time.time()
        self.state = JobState.RUNNING
        self.iterator()
    
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
        self.endTime = time.time()
        self.state = JobState.COMPLETE
        self.dump()
    
    
    # default callback which handles bookkeeping.  derived classes
    # can re-implement callback() but should probably call this method
    # via super(), or else duplicate the bookkeeping code
    def callback(self, value):        
        self.iterations = self.iterations + 1
        self.bytesTransferred = self.bytesTransferred + len(value)
        self.elapsedTime = time.time() - self.startTime
    
    
    # default errback -- see comments for callback()
    def errback(self, value):
        self.elapsedTime = time.time() - self.startTime
        self._errors = self._errors + 1


    # dump job information to the console.  useful for debugging.
    def dump(self):
        print "state: %s" % self.state
        print "start time: %s, end time: %s, elapsed time: %s" % (self.startTime, self.endTime, self.elapsedTime)
        print "bytes transferred: %s" % self.bytesTransferred
        print "iterations: %s" % self.iterations


    # handy method to set up a Deferred and set up callbacks.  this needs to be
    # a separate method so it can easily be triggered by reactor.callLater
    def _request(self, host, port, url):
        factory = HTTPClientFactory(url, agent=self.userAgent)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback)
        factory.deferred.addErrback(self.errback)
