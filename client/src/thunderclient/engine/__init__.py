from Queue import Queue
from twisted.internet import reactor
from time import sleep

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage

from zope.interface import Interface

from hammerengine import HammerEngine
from randomengine import RandomEngine

class IEngineFactory(Interface):
    def start(self):
        pass
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def stop(self):
        pass

class EngineFactory(object):
    @staticmethod
    def createFactory():
        if True:
            return HammerEngine()
        else:
            return RandomEngine()
