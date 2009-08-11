from Queue import Queue
from twisted.internet import reactor
import random
import time
import math

from zope.interface import Interface, Attribute, implements

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage
from twisted.web.client import _parse

from traffic import TrafficEngine
from hammer import HammerEngine

from ..orchestrator.job import IJob
from ..orchestrator.job import JobSpec, JobState, JobResults

class EngineFactory(object):
    @staticmethod
    def createFactory(jobSpec):
        return HammerEngine(jobSpec)

#class IEngine(Interface):
#    clients = Attribute("""foo""")
    
#    def results(self):
#        """Generate a JobResult object"""
