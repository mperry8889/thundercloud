from thunderserver.db import dbConnection as db
from thunderserver.orchestrator.user import UserManager, UserPerspective, UserAlreadyExists, NoSuchUser
from thundercloud.spec.user import UserSpec

from thunderserver.authentication.job import JobDBChecker
from thunderserver.authentication.slave import SlaveDBChecker

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.internet.defer import DeferredList, Deferred, inlineCallbacks, returnValue

import crypt

class HttpAuthTestMixin(object):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass