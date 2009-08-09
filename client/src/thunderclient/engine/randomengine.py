from zope.interface import implements

from . import IEngineFactory

class RandomEngine(object):
    implements(IEngineFactory)