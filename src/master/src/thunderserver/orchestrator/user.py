from ..db import dbConnection as db
from thundercloud.spec.user import UserSpec

from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.internet import reactor

import crypt
import random

import logging

log = logging.getLogger("orchestrator.user")

class NoSuchUser(Exception):
    pass

class UserAlreadyExists(Exception):
    pass

class WeakPassword(Exception):
    pass

class InvalidPassword(Exception):
    pass

class UserPerspective(object):
    def __init__(self, userSpec):
        self.userSpec = userSpec


class _UserManager(object):
    def __init__(self):
        pass
    
    def _checkUser(self, username):
        # check if user exists
        rows = db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchall()
        d = Deferred()
        
        if len(rows) < 1:
            reactor.callLater(0, d.callback, False)
        else:
            assert len(rows) == 1
            reactor.callLater(0, d.callback, True)
            
        return d
        
    @inlineCallbacks
    def create(self, userSpec):
        request = self._checkUser(userSpec.username)
        yield request
        if request.result is True:
            raise UserAlreadyExists
        
        # XXX fix salt, perhaps even the double-query
        db.execute("INSERT INTO users (username, password, userspec) VALUES (?, ?, ?)", (userSpec.username, crypt.crypt(userSpec.password, "ab"), userSpec))
        userId = int(db.execute("SELECT id FROM users WHERE username = ?", (userSpec.username,)).fetchall()[0]["id"])

        returnValue(userId)
    
    @inlineCallbacks
    def delete(self, username):
        request = self._checkUser(username)
        yield request
        if request.result is False:
            raise NoSuchUser

        db.execute("UPDATE users SET deleted = 't' WHERE username = ?", (username,))

        returnValue(True)


    def get(self, username):
        rows = db.execute("SELECT userSpec FROM users WHERE username = ?", (username,)).fetchall()
        if len(rows) < 1:
            raise NoSuchUser
        assert len(rows) == 1
        
        row = rows[0]
        userSpec = row["userspec"]
        userObj = _User(userSpec)
        #userObj.validate()
        
        d = Deferred()
        reactor.callLater(0, d.callback, userObj)
        return d
 
UserManager = _UserManager()