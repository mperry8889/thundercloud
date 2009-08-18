from zope.interface import Interface

from thundercloud import constants

class InvalidJobSpec(Exception):
    def __init__(self, msg):
        self.msg = msg

class JobSpec(object):
    class JobProfile:
        HAMMER = 0
        BENCHMARK = 1

    requests = {"":{}}
    duration = float("inf")
    transferLimit = float("inf")
    clientFunction = "1"
    statsGranularity = 60
    userAgent = "thundercloud client/%s" % constants.VERSION
    profile = JobProfile.HAMMER

    def __init__(self, json=None):
        if json is None: return
        for key in json.keys():
            setattr(self, key, json[key])

    # verify rules for job specs are adhered to
    def validate(self):
        # can't have an infinite transfer limit and infinite duration
        if self.duration == float("inf") and self.transferLimit == float("inf"):
            raise InvalidJobSpec("Must set a duration or transfer limit")
    
        # stats granularity must be an int
        if type(self.statsGranularity) != int:
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
        
        # profile has to be valid
        if self.profile != JobSpec.JobProfile.BENCHMARK and \
           self.profile != JobSpec.JobProfile.HAMMER:
            raise InvalidJobSpec("Invalid job profile")
        
        # if everything is ok...
        return True


class JobResults(object):
    iterations = 0
    bytesTransferred = 0
    elapsedTime = 0
    statisticsByTime = {}
    errors = {}


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
