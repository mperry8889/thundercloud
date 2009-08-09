from twisted.web.client import HTTPClientFactory
from zope.interface import implements
from Queue import Queue

from ..orchestrator.job import IJob
from . import IEngine

class HammerEngine(object):
    implements(IJob)
    implements(IEngine)
    
    def __init__(self):
        pass
    
    def start(self):
        pass
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def stop(self):
        pass