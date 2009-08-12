from benchmark import BenchmarkEngine
from hammer import HammerEngine


class EngineFactory(object):
    @staticmethod
    def createFactory(jobSpec):
        return BenchmarkEngine(jobSpec)