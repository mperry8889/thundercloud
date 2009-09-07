from thundercloud.dataobject import DataObject

class SlaveSpec(DataObject):
    _attributes = {
        "scheme:": "http",
        "host": None,
        "port": None,
        "path": None,
    }