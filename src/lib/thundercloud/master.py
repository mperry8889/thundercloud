from thundercloud.dataobject import DataObject

class MasterSpec(DataObject):
    _attributes = {
        "host": None,
        "port": None,
        "path": None,
    }