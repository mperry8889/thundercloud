from thunderserver.db import dbConnection as db
from thunderserver.orchestrator.user import UserManager, UserPerspective, UserAlreadyExists, NoSuchUser
from thundercloud.spec.user import UserSpec

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.internet.defer import DeferredList, Deferred, inlineCallbacks, returnValue

import crypt

class UserManagerTestMixin(object):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        #db.execute("DELETE FROM users WHERE username <> 'SLAVE'")
    

class LifeCycle(UserManagerTestMixin, unittest.TestCase):
    
    def setUp(self):
        return super(LifeCycle, self).setUp()
    
    def _verifyUser(self, userId, userSpec):
        rows = db.execute("SELECT id, username, password FROM users WHERE username = ?", (userSpec.username,)).fetchall()
        self.assertEquals(len(rows), 1)
        
        row = rows[0]
        self.assertEquals(row["id"], userId)
        self.assertEquals(row["username"], userSpec.username)
        self.assertEquals(row["password"], crypt.crypt(userSpec.password, row["password"]))
        return userId

    def _verifyDeleted(self, value, userId):
        rows = db.execute("SELECT id, deleted FROM users WHERE id = ?", (userId,)).fetchall()
        self.assertEquals(len(rows), 1)
        
        row = rows[0]
        self.assertEquals(str(row["deleted"]), "t")
        return userId
    
    def _createUserSpec(self, username, password):
        userSpec = UserSpec()
        userSpec.username = username
        userSpec.password = password
        return userSpec
    
    def test_createUser(self):
        """Create a basic, no frills user"""
        userSpec = self._createUserSpec("test_createUser", "foo")
        deferred = UserManager.create(userSpec)
        deferred.addCallback(self._verifyUser, userSpec)
        return deferred
    
    @inlineCallbacks
    def test_createDuplicate(self):
        """Create a duplicate user"""
        userSpec = self._createUserSpec("test_createDuplicate", "foo")
        deferred = UserManager.create(userSpec)
        deferred.addCallback(self._verifyUser, userSpec)
        yield deferred
        yield self.failUnlessFailure(UserManager.create(userSpec), UserAlreadyExists)
        returnValue(None)

    @inlineCallbacks
    def test_delete(self):
        """Delete a user"""
        userSpec = self._createUserSpec("test_delete", "foo")
        deferred = UserManager.create(userSpec)
        deferred.addCallback(self._verifyUser, userSpec)
        yield deferred
        
        userId = deferred.result
        deferred2 = UserManager.delete(userSpec.username)
        deferred2.addCallback(self._verifyDeleted, userId)
        yield deferred2
        returnValue(None)
    
    def test_deleteInvalid(self):
        """Delete an invalid user"""
        return self.failUnlessFailure(UserManager.delete("aasdfasdfasdfsadfsfd"), NoSuchUser)

        
        