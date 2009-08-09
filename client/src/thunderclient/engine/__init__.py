from Queue import Queue
from twisted.internet import reactor
from time import sleep

from zope.interface import Interface, Attribute

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage

from hammer import HammerEngine

class IEngine(Interface):
    clients = Attribute("""foo""")

class EngineFactory(object):
    @staticmethod
    def createFactory(**kwargs):
        return HammerEngine()