from thundercloud.dataobject import DataObject

class SlaveSpec(DataObject):
    _attributes = {
        "host": None,
        "port": None,
        "path": None,
    }
                   