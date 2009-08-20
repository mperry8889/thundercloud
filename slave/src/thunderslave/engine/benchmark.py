from Queue import Queue, Empty
import math
import time
import random

from twisted.internet import reactor

from enginebase import EngineBase
from thundercloud.job import JobState
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

class BenchmarkEngine(EngineBase):

    def __init__(self, jobSpec):
        super(BenchmarkEngine, self).__init__(jobSpec)
        self.iterator = self._loop
        self.userAgent = "thundercloud traffic simulation client/%s" % constants.VERSION
        self.delay = DelayFactory.createFactory(0.0)
        self.clients = 0

    # find out the number of clients needed at the current time, and add clients
    # until the max number of clients is reached
    def _loop(self):
        if self.state == JobState.RUNNING:
            # calculates client function at time t
            clientFunctionResult = min(constants.CLIENT_UPPER_BOUND, abs(int(math.ceil(self.clientFunction(time.time())))))
            
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
                    #
                    # queue may be empty if there are no URLs in the job spec
                    try:
                        request = self.httpClientRequestQueue.get(False)
                    except Empty:
                        self.stop()
                        return
                    self.httpClientRequestQueue.put(request)
                    self.clients = self.clients + 1
                    reactor.callLater(self.delay(), self._request, 
                                      request[0], request[1], request[2],
                                      request[3], request[4], request[5])
                        

    # after each request is processed, do some calculations and spin up some
    # new requests if the test is going to continue
    def callback(self, value, requestTime):
        super(BenchmarkEngine, self).callback(value, requestTime)
        self.clients = self.clients - 1
        
        # just bail if the job isn't running anymore
        if self.state != JobState.RUNNING:
            return
            
        # otherwise keep it going
        else:
            self._loop()


    def errback(self, value, requestTime):
        super(BenchmarkEngine, self).errback(value, requestTime)
        self.clients = self.clients - 1
    
