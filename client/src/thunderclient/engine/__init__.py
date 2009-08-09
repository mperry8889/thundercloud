from Queue import Queue
from twisted.internet import reactor
import time

from zope.interface import Interface, Attribute, implements

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage

from ..orchestrator.job import IJob
from ..orchestrator.job import JobSpec, JobState, JobResults

class EngineFactory(object):
    @staticmethod
    def createFactory(jobSpec):
        return _Engine()

class IEngine(Interface):
    clients = Attribute("""foo""")
    
    def results(self):
        """Generate a JobResult object"""

class _Engine(object):
    implements(IEngine)
    implements(IJob)
    
    _clientFunction = lambda: 1
    _transferLimit = None
    _requests = []
    _duration = 0
    _delay = 0.0

    _startTime = time.time()
    _endTime = None
    _elapsedTime = 0.0
    
    _transfer = 0.0
    _clients = 0
    
    _state = JobState.NEW
    
    def __init__(self, jobSpec):
#        self._clientFunction = eval("lambda t: abs(%s)" % jobSpec.simultaneousClientFunction)
#        self._requests = jobSpec.requests
#        self._duration = jobSpec.testDuration
#        self._delay = jobSpec.delayBetweenRequests
        self._requests = {
            "http://unshift.net": {
             "httpMethod": "GET",
             "httpUserAgent": "thunderclient 1.0",
             "httpCookie": None,
             "httpCustomHeaders": None,
             "timeout": 10,
            },
            "http://unshift.net/temp": {
             "httpMethod": "GET",
             "httpUserAgent": "thunderclient 1.0",
             "httpCookie": None,
             "httpCustomHeaders": None,
             "timeout": 10,
            },
            "http://unshift.net/projects": {
             "httpMethod": "GET",
             "httpUserAgent": "thunderclient 1.0",
             "httpCookie": None,
             "httpCustomHeaders": None,
             "timeout": 10,
            },
        }
    
    def start(self):
        self._startTime = time.time()
        self._state = JobState.RUNNING
        clients = self._clientFunction(0)
        if clients <= 0:
            clients = 1
        
        for i in range(0, clients):
            pass
            
    
    def pause(self):
        self._state = JobState.PAUSED
    
    def resume(self):
        self._state = JobState.RUNNING
    
    def stop(self):
        self._endTime = time.time()
        self._state = JobState.COMPLETE
    
    def state(self):
        return self._state
    
    def results(self):
        pass
    
    def callback(self, value, time):
        pass
    
    def errback(self, value, time):
        pass