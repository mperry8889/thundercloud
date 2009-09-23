from dataobject import DataObject

import simplejson as json
import sqlite3

class UserSpec(DataObject):
    _attributes = {
        "username": None,
        "password": None,
        "jobs": None,
        "lastLogin": None,  
    }

sqlite3.register_converter("userSpec", lambda s: UserSpec(json.loads(s)))