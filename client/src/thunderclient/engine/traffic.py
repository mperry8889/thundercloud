from Queue import Queue
import math
import time
import random

from twisted.internet import reactor

from enginebase import EngineBase
from ..orchestrator.job import JobState
from thundercloud import constants

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

class TrafficEngine(EngineBase):

    # find out the number of clients needed at the current time, and add clients
    # until the max number of clients is reached
    def _loop(self):
        if self.state == JobState.RUNNING:
            # calculates client function at time t
            clientFunctionResult = abs(int(math.ceil(self.clientFunction(self.elapsedTime))))
            
            # only add clients if clientFunc(t) calls for more clients than are
            # currently in the system.  this may not always be the case -- if a 
            # traffic slowdown is being simulated, clients in the system need to
            # die off.  an example of this is a sine wave; at t=1 there will be more
            # clients than t=1.5
            if clientFunctionResult > self.clients:
                for i in range(self.clients, clientFunctionResult):
                    # take a request item off the queue and then move it right up top.
                    # this seems nonsensical but it makes the clients fetch all the URLs
                    # in the order of the queue, and easily allows n clients to handle n+1
                    # URLs
                    request = self.httpClientRequestQueue.get()
                    self.httpClientRequestQueue.put(request)
                    self.clients = self.clients + 1
                    reactor.callLater(self.delay(), self._request, request[0], request[1], request[2])
                        

    # after each request is processed, do some calculations and spin up some
    # new requests if the test is going to continue
    def callback(self, value):        
        super(TrafficEngine, self).callback(value)
        self.clients = self.clients - 1
        
        # just bail if the job isn't running anymore
        if self.state != JobState.RUNNING:
            return
        
        # if we're over time, also bail
        if self.elapsedTime >= self.duration:
            self.stop()
            
        # otherwise keep it going
        else:
            self._loop()


    def errback(self, value):
        super(TrafficEngine, self).errback(value)
        self.clients = self.clients - 1

    
    iterator = _loop
    delay = DelayFactory.createFactory(0.0)
    clients = 0
    userAgent = "thundercloud traffic simulation client/%s" % constants.VERSION
        
    
