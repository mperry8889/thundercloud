from traffic import TrafficEngine
from hammer import HammerEngine


class EngineFactory(object):
    @staticmethod
    def createFactory(jobSpec):
        return TrafficEngine(jobSpec)