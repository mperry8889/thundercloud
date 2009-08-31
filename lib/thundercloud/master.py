from thundercloud.util import DataObject

class MasterSpec(DataObject):
    _attributes = {
        "host": None,
        "port": None,
        "path": None,
    }