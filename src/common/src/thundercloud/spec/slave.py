from thundercloud.spec.dataobject import DataObject

import logging
log = logging.getLogger("slaveInfo")


class SlaveState(DataObject):
    CONNECTED = 0
    IDLE = 1
    ALLOCATED = 2
    RUNNING = 3
    DISCONNECTED = 4
    UNKNOWN = 9999

    _attributes = {
        "state": IDLE,
        "jobCount": 0,
    }
    
    def jobCount(self):
        return self.jobCount
    
    def increment(self):
        self.jobCount += 1
    
    def decrement(self):
        self.jobCount -= 1
        if self.jobCount < 0:
            log.error("Slave job count is < 0, this should not happen")
    

class SlaveSpec(DataObject):
    _attributes = {
        "scheme": "http",
        "host": None,
        "port": None,
        "path": None,
        
        "connectionSpeed": None,
        "maxRequestsPerSec": None,
        
        "location": {
            "latitude": None,
            "longitude": None,
            "city": None,
            "state": None,
        },
    }

    def validate(self):
        return True