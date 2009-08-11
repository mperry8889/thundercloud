from Queue import Queue
from twisted.internet import reactor
import random
import time
import math

from zope.interface import Interface, Attribute, implements

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage
from twisted.web.client import _parse

#from . import IEngine
from ..orchestrator.job import IJob
from ..orchestrator.job import JobSpec, JobState, JobResults

class DelayFactory(object):
    @classmethod
    def createFactory(self, delay):
        if type(delay) == float or type(delay) == int:
            return FloatDelay(float(delay))
        else:
            return RandomDelay(delay)

class FloatDelay(object):
    def __init__(self, delay):
        self.delay = delay
    def __call__(self):
        return self.delay

class RandomDelay(object):
    def __init__(self, boundary):
        self.boundary = boundary
    def __call__(self):
        return random.uniform(0, self.boundary)

class TrafficEngine(object):
    implements(IJob) #IEngine

    _clientFunction = lambda self, t: 2*t
    _transferLimit = None
    _requests = []
    _duration = 60
    _delay = DelayFactory.createFactory(0.0)

    _startTime = time.time()
    _endTime = None
    _elapsedTime = 0.000001
    
    _bytesTransferred = 0.0
    _clients = 0
    _iterations = 0
    
    _state = JobState.NEW
    
    _httpClientRequestQueue = Queue()
    
    def __init__(self, jobSpec):
#        self._clientFunction = eval("lambda self, t: abs(%s)" % jobSpec.simultaneousClientFunction)
#        self._requests = jobSpec.requests
#        self._duration = jobSpec.testDuration
#        self._delay = jobSpec.delayBetweenRequests
        self._requests = {
            "http://www.gaiasearch.com": {},
            "http://unshift.net": {},
            "http://dev.unshift.net": {},
        }
        
        # dump the host/port/URLs to be fetched into a queue
        for url in self._requests.keys():
            scheme, host, port, path = _parse(url)
            self._httpClientRequestQueue.put([host, port, url])

    
    # start the engine.  set the current time and set the job state as running,
    # then spin up all of the clients
    def start(self):
        self._startTime = time.time()
        self._state = JobState.RUNNING
        
        self._spinUpRequests()

    
    # handy method to set up a Deferred and set up callbacks.  this needs to be
    # a separate method so it can easily be triggered by reactor.callLater
    def _request(self, host, port, url):
        factory = HTTPClientFactory(url)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback)
        factory.deferred.addErrback(self.errback)
      
        
    # find out the number of clients needed at the current time, and add clients
    # until the max number of clients is reached
    def _spinUpRequests(self):
        if self._state == JobState.RUNNING:
            # calculates client function at time t
            clientFunctionResult = int(math.ceil(self._clientFunction(self._elapsedTime)))
            
            # only add clients if clientFunc(t) calls for more clients than are
            # currently in the system.  this may not always be the case -- if a 
            # traffic slowdown is being simulated, clients in the system need to
            # die off.  an example of this is a sine wave; at t=1 there will be more
            # clients than t=1.5
            if clientFunctionResult > self._clients:
                for i in range(self._clients, clientFunctionResult):
                    # take a request item off the queue and then move it right up top.
                    # this seems nonsensical but it makes the clients fetch all the URLs
                    # in the order of the queue, and easily allows n clients to handle n+1
                    # URLs
                    request = self._httpClientRequestQueue.get()
                    self._httpClientRequestQueue.put(request)
                    self._clients = self._clients + 1
                    reactor.callLater(self._delay(), self._request, request[0], request[1], request[2])
                        

    # after each request is processed, do some calculations and spin up some
    # new requests if the test is going to continue
    def callback(self, value):        
        self._clients = self._clients - 1
        self._iterations = self._iterations + 1
        self._bytesTransferred = self._bytesTransferred + len(value)
        self._elapsedTime = time.time() - self._startTime
        
        #self.dump()
        
        # just bail if the job isn't running anymore
        if self._state != JobState.RUNNING:
            return
        
        # if we're over time, also bail
        if self._elapsedTime >= self._duration:
            self.stop()
            
        # otherwise keep it going
        else:
            self._spinUpRequests()
    
    def errback(self, value):
        self._clients = self._clients - 1
        self._elapsedTime = time.time() - self._startTime
        print value
        #self.dump()


    def pause(self):
        self._state = JobState.PAUSED
    
    def resume(self):
        self._state = JobState.RUNNING
        
        self._spinUpRequests()
    
    def stop(self):
        self._endTime = time.time()
        self._state = JobState.COMPLETE
        self.dump()
    
    def state(self):
        return self._state
    
    def results(self):
        pass
    
    def dump(self):
        print "iterations: %s" % self._iterations
        print "elapsed time: %s" % self._elapsedTime
        print "bytes transferred: %s" % self._bytesTransferred
        print "concurrent clients: %s" % self._clients
        print "state: %s" % self._state
