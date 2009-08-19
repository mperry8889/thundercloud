from benchmark import BenchmarkEngine
from hammer import HammerEngine
from thundercloud.job import JobSpec

class EngineFactory(object):
    @staticmethod
    def createFactory(jobSpec):
        if jobSpec.profile == JobSpec.JobProfile.BENCHMARK:
            return BenchmarkEngine(jobSpec)
        elif jobSpec.profile == JobSpec.JobProfile.HAMMER:
            return HammerEngine(jobSpec)