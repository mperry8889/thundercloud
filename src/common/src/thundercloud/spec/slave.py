from thundercloud.spec.dataobject import DataObject

class SlaveState(object):
    DISCONNECTED = 0
    CONNECTED = 1
    IDLE = 2
    WORKING = 3
    UNKNOWN = 9999

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