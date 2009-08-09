from zope.interface import implements

from ..orchestrator.job import IJob

class RandomEngine(object):
    implements(IJob)