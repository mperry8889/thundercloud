from zope.interface import Interface
import simplejson as json
import jsonpickle
import sqlite3

from thundercloud import constants

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
    
    def results(self):
        """Get job results"""


class InvalidJobSpec(Exception):
    def __init__(self, msg):
        self.msg = msg

class JobSpec(object):
    class JobProfile:
        HAMMER = 0
        BENCHMARK = 1
        DUMMY = 9999
    
    __attributes = {"requests": {"":{}},
                    "duration": float("inf"),
                    "transferLimit": float("inf"),
                    "clientFunction": "1",
                    "statsInterval": float("inf"),
                    "userAgent": "thundercloud client/%s" % constants.VERSION,
                    "profile": JobProfile.HAMMER,
                    "state": JobState.NEW,
    }                

    def __init__(self, json=None):
        for key in self.__attributes.keys():
            setattr(self, key, self.__attributes[key])
        if json is not None: self.slurp(json)

    # representation: dictionary object
    def __repr__(self):
        obj = {}
        for key in self.__attributes.keys():
            try:
                obj.update({ key: getattr(self, key) })
            except AttributeError:
                pass
        return obj
    
    # string representation: stringified JSON
    def __str__(self):
        return json.dumps(self.toJson())
    
    # used for SQLite adaptation
    def __conform__(self, protocol):
        if protocol == sqlite3.PrepareProtocol:
            return self.__str__()

    # json representation
    def toJson(self):
        return jsonpickle.Pickler(unpicklable=True).flatten(self.__repr__())    
    
    # conveniently import JSON
    def slurp(self, json):
        if json is None: return
        for key in json.keys():
            setattr(self, key, json[key])


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



class JobResults(object):
    __attributes = {     
        "jobId": 0,
        "state": None,
        "iterations": 0,
        "transferLimit": 0,
        "bytesTransferred": 0,
        "duration": 0,
        "elapsedTime": 0,
        "statisticsByTime": {},
        "errors": {},
    }

    def __init__(self, json=None):
        for key in self.__attributes.keys():
            setattr(self, key, self.__attributes[key])
        if json is not None: self.slurp(json)

    # representation: dictionary object
    def __repr__(self):
        obj = {}
        for key in self.__attributes.keys():
            try:
                obj.update({ key: getattr(self, key) })
            except AttributeError:
                pass
        return obj
    
    # string representation: stringified JSON
    def __str__(self):
        return json.dumps(self.toJson())
    
    # used for SQLite adaptation
    def __conform__(self, protocol):
        if protocol == sqlite3.PrepareProtocol:
            return self.__str__()

    # json representation
    def toJson(self):
        return jsonpickle.Pickler(unpicklable=True).flatten(self.__repr__())    
    
    # conveniently import JSON
    def slurp(self, json):
        if json is None: return
        for key in json.keys():
            setattr(self, key, json[key])

sqlite3.register_converter("jobResults", lambda s: JobResults(json.loads(s)))
