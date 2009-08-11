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


class HammerEngine(object):
    implements(IJob) #IEngine

    _clientFunction = lambda self, t: 10#t*math.sin(t)
    _transferLimit = None
    _duration = 60

    _startTime = time.time()
    _endTime = None
    _elapsedTime = 0.000001
    
    _bytesTransferred = 0.0
    _iterations = 0
    _errors = 0
    
    _state = JobState.NEW
    
    _httpClientRequestQueue = Queue()
    
    def __init__(self, jobSpec):
#        self._clientFunction = eval("lambda self, t: abs(%s)" % jobSpec.simultaneousClientFunction)
#        self._requests = jobSpec.requests
#        self._duration = jobSpec.testDuration
#        self._delay = jobSpec.delayBetweenRequests
        self._requests = {
            "http://192.168.1.100":{},
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

        self._loop()

    # handy method to set up a Deferred and set up callbacks.  this needs to be
    # a separate method so it can easily be triggered by reactor.callLater
    def _request(self, host, port, url):
        factory = HTTPClientFactory(url)
        reactor.connectTCP(host, port, factory)
        factory.deferred.addCallback(self.callback)
        factory.deferred.addErrback(self.errback)


    # dump a bunch of requests into the reactor, scheduling them evenly over the next 
    # second.  then schedule another loop for a second later
    def _loop(self):
        self._elapsedTime = time.time() - self._startTime
        
        self.dump()
        
        if self._elapsedTime >= self._duration:
            self.stop()
            return
        
        if self._state == JobState.RUNNING:
            numRequests = abs(int(math.ceil(self._clientFunction(self._elapsedTime))))
            try:
                timeBetween = 1.0/numRequests
            except ZeroDivisionError:
                reactor.callLater(0, self._loop)   # avoid recursing
                return
            print "making %d requests at %f sec delay" % (numRequests, timeBetween)
            for i in range(0, numRequests):
                request = self._httpClientRequestQueue.get()
                self._httpClientRequestQueue.put(request)
                reactor.callLater(timeBetween, self._request, request[0], request[1], request[2])
            reactor.callLater(1, self._loop)


    def callback(self, value):        
        self._iterations = self._iterations + 1
        self._bytesTransferred = self._bytesTransferred + len(value)
        self._elapsedTime = time.time() - self._startTime
    
    def errback(self, value):
        self._elapsedTime = time.time() - self._startTime
        self._errors = self._errors + 1
        #self.dump()  

    def pause(self):
        self._state = JobState.PAUSED
    
    def resume(self):
        self._state = JobState.RUNNING
        self._loop()
    
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
        print "errors: %s" % self._errors
        print "elapsed time: %s" % self._elapsedTime
        print "bytes transferred: %s" % self._bytesTransferred
        print "state: %s" % self._state
