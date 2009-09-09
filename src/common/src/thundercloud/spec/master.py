from thundercloud.spec.dataobject import DataObject

class MasterSpec(DataObject):
    _attributes = {
        "scheme:": "http",
        "host": None,
        "port": None,
        "path": None,
    }
    
    def validate(self):
        return True