from zope.interface import Interface

class JobSpec(object):
    requests = [{"URL": None,
                 "httpMethod": "GET",
                 "httpUserAgent": None,
                 "httpPostData": None,
                 "httpCustomHeaders": None,
                 "httpCookie": None,
                 "timeout": 0,
               },]
    
    testDuration = None
    simultaneousClientFunction = None
    delayBetweenRequests = 0
    

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
