from Queue import Queue
from twisted.internet import reactor
import time
import math

from twisted.web.client import HTTPClientFactory
from twisted.web.client import _parse

from enginebase import EngineBase
from thundercloud.job import JobState
from thundercloud import constants

class HammerEngine(EngineBase):

    # dump a bunch of requests into the reactor, scheduling them evenly over the next 
    # second.  then schedule another loop for a second later
    def _loop(self):
        self.elapsedTime = time.time() - self.startTime
        
        if self.bytesTransferred >= self.transferLimit:
            self.stop()
            return
        
        if self.elapsedTime >= self.duration:
            self.stop()
            return
        
        if self.state == JobState.RUNNING:
            numRequests = min(constants.CLIENT_UPPER_BOUND, abs(int(math.ceil(self.clientFunction(time.time())))))
            try:
                timeBetween = 1.0/numRequests
            except ZeroDivisionError:
                reactor.callLater(0, self._loop)   # avoid recursing
                return
            for i in range(0, numRequests):
                request = self.httpClientRequestQueue.get()
                self.httpClientRequestQueue.put(request)
                reactor.callLater(timeBetween, self._request, request[0], request[1], request[2])
            reactor.callLater(1, self.iterator)
            

    iterator = _loop
    userAgent = "thundercloud hammer client/%s" % constants.VERSION