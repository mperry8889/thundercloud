from thunderslave.engine.base import EngineBase
from thunderslave.engine.hammer import HammerEngine

from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

from twisted.trial import unittest

class TestEngine(HammerEngine):
    def _request(self, host, port, method, url, postdata, cookies):
        d = Deferred()
        d.addCallback(self._callback)
        d.addErrback(self._callback)
        reactor.callLater(0, d.callback, {})
        
        #self.value = {
        #    "startTime": time.time(),
        #    "timeToConnect": 0,
        #    "timeToFirstByte": 0,
        #    "elapsedTime": 0,
        #    "bytesTransferred": 0,
        #}

class EngineTestMixin(object):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

