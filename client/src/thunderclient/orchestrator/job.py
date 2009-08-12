from zope.interface import Interface

from thundercloud import constants

class JobSpec(object):
    requests = {}
    duration = None
    transferLimit = float("inf")
    clientFunction = lambda self, t: False
    userAgent = "thundercloud client/%s" % constants.VERSION


class JobResults(object):
    bytesTransferred = 0
    httpResponses = {"Code": 0}
    responseTime = {
        "time": {
            "min": None,
            "max": None,
            "avg": None,
            "stddev": None,
        }
    }


class JobState(object):
    NEW = 0
    RUNNING = 1
    PAUSED = 2
    COMPLETE = 3


class IJob(Interface):
    def start(self):
        """Start"""
    
    def pause(self):
        """Pause"""
    
    def resume(self):
        """Resume"""
    
    def stop(self):
        """Stop"""
    
    def state(self):
        """Get job state"""
