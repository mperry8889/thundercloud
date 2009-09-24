from zope.interface import implements, Interface
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred import error, credentials
from twisted.internet import defer
from twisted.python import failure
import crypt

import logging

log = logging.getLogger("auth.DBChecker")

class UserNotFound(Exception):
    pass

class IDBChecker(Interface):
    def getUserAndPassword(self, username): pass


class DBChecker(object):
    implements(ICredentialsChecker)
    
    # we're using HTTP BASIC auth, and passwords are hashed in the DB,
    # so we can only accept plaintext passwords
    credentialInterfaces = (credentials.IUsernamePassword,)
    
    def __init__(self, dbHandle):
        self.db = dbHandle
    
    # this needs to be implemented by subclasses
    def getUserAndPassword(self, username):
        raise NotImplementedException
    
    def requestAvatarId(self, creds):
        log.debug("Authenticating user %s" % creds.username)
        try:
            (username, dbPassword) = self.getUserAndPassword(creds.username)
        except:
            return defer.fail(error.UnauthorizedLogin())

        if crypt.crypt(creds.password, dbPassword) == dbPassword:
            log.debug("User authenticated")
            return defer.succeed(creds.username)
        else:
            log.debug("User authentication failed")
            return defer.fail(error.UnauthorizedLogin())
