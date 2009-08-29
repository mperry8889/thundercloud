from benchmark import BenchmarkEngine
from hammer import HammerEngine
from dummy import DummyEngine
from thundercloud.job import JobSpec

class EngineFactory(object):
    @staticmethod
    def createFactory(jobId, jobSpec):
        if jobSpec.profile == JobSpec.JobProfile.BENCHMARK:
            return BenchmarkEngine(jobId, jobSpec)
        elif jobSpec.profile == JobSpec.JobProfile.HAMMER:
            return HammerEngine(jobId, jobSpec)
        elif jobSpec.profile == JobSpec.JobProfile._DUMMY:
            return DummyEngine(jobId, jobSpec)