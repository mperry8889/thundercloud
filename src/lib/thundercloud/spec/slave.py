from thundercloud.spec.dataobject import DataObject

class SlaveSpec(DataObject):
    _attributes = {
        "scheme:": "http",
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