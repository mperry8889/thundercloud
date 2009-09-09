from zope.interface import Interface
import simplejson as json
import jsonpickle
import sqlite3

from thundercloud import constants
from thundercloud.spec.dataobject import DataObject

class JobState(object):
    NEW = 0
    RUNNING = 1
    PAUSED = 2
    COMPLETE = 3
    UNKNOWN = 9999

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
    
    def results(self):
        """Get job results"""


class InvalidJobSpec(Exception):
    def __init__(self, msg):
        self.msg = msg

class JobSpec(DataObject):
    class JobProfile:
        HAMMER = 0
        BENCHMARK = 1
        DUMMY = 9999
    
    _attributes = {
        "requests": {"":{}},
        "duration": float("inf"),
        "transferLimit": float("inf"),
        "clientFunction": "1",
        "statsInterval": float("inf"),
        "userAgent": str("thundercloud client/%s" % constants.VERSION),
        "profile": JobProfile.HAMMER,
        "state": JobState.NEW,
        "timeout": float("inf"),
    }                

    # verify rules for job specs are adhered to
    def validate(self):
        # can't have an infinite transfer limit and infinite duration
        if self.duration == float("inf") and self.transferLimit == float("inf"):
            raise InvalidJobSpec("Must set a duration or transfer limit")
    
        # stats granularity must be an int
        if type(self.statsInterval) != int:
            raise InvalidJobSpec("Invalid stats granularity")
    
        # client function has to use t as an argument
        
        # requests must be a dict of URLs to well-formed request objects
        if type(self.requests) != dict:
            raise InvalidJobSpec("Requests must be a well-formed dictionary")
        for request in self.requests:
            if type(self.requests[request]) != dict:
                raise InvalidJobSpec("Malformed request")
            if not self.requests[request].has_key("method")   or \
               not self.requests[request].has_key("postdata") or \
               not self.requests[request].has_key("cookies"):
                raise InvalidJobSpec("Malformed request, missing key")
        
        # if request dict is empty, spec is invalid
        if self.requests == {"":{}} or self.requests == {}:
            raise InvalidJobSpec("No URLs requested")
        
        # profile has to be valid
        if self.profile != JobSpec.JobProfile.BENCHMARK and \
           self.profile != JobSpec.JobProfile.HAMMER:
            raise InvalidJobSpec("Invalid job profile")
        
        # if everything is ok...
        return True

sqlite3.register_converter("jobSpec", lambda s: JobSpec(json.loads(s)))



class JobResults(DataObject):
    _attributes = {     
        "jobId": 0,
        "state": None,
        "iterations": 0,
        "transferLimit": 0,
        "bytesTransferred": 0,
        "duration": 0,
        "elapsedTime": 0,
        "statisticsByTime": {"":{}},
        "errors": {},
        "requestsCompleted": 0,
        "requestsFailed": 0,
        "nodes": 0,
    }

sqlite3.register_converter("jobResults", lambda s: JobResults(json.loads(s)))
