from Queue import Queue, Empty
from twisted.internet import reactor
import time
import math

from base import EngineBase
from thundercloud.job import JobState
from thundercloud import constants

class HammerEngine(EngineBase):

    def __init__(self, jobId, jobSpec):
        super(HammerEngine, self).__init__(jobId, jobSpec)
        self.iterator = self._loop

    # dump a bunch of requests into the reactor, scheduling them evenly over the next 
    # second.  then schedule another loop for a second later
    def _loop(self):
        self.elapsedTime = time.time() - self.startTime - self.pausedTime
        
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
                # queue may be empty if there are no URLs in the job spec
                try:
                    request = self.httpClientRequestQueue.get(False)
                except Empty:
                    self.stop()
                    return
                self.httpClientRequestQueue.put(request)
                reactor.callLater(timeBetween, self._request, 
                                  request[0], request[1], request[2],
                                  request[3], request[4], request[5])
            reactor.callLater(1, self.iterator)