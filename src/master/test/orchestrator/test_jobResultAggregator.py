from thunderserver.orchestrator.job import AggregateJobResults
from thundercloud.spec.job import JobState, JobResults
from thundercloud.spec.dataobject import DataObject

from twisted.trial import unittest


class AggregateJobResultsTestMixin(object):
    def setUp(self):
        self.aggregateResults = AggregateJobResults()
    
    def tearDown(self):
        pass

class Basic(AggregateJobResultsTestMixin, unittest.TestCase):
            
    def test_singleShortResult(self):
        """Test a single short result, no merge necessary"""
        raise NotImplementedError
    
    def test_singleLongResult(self):
        """Test a single long result, no merge necessary"""
        raise NotImplementedError
    
    def test_mergeMultipleShortResults(self):
        """Merge 3 short results"""
        raise NotImplementedError
    
    def test_mergeMultipleLongResults(self):
        """Merge 3 long results"""
        raise NotImplementedError
    
    def test_mergeSlaveDropoff(self):
        """Merge results with a slave drop-off, leading to a lack of status from a slave during some time period"""
        raise NotImplementedError
    
    def test_mergeMixedElapsedTime(self):
        """Check that wildly varying elapsed times are handled correctly"""
        raise NotImplementedError

class JobStates(AggregateJobResultsTestMixin, unittest.TestCase):
    
    def test_same(self):
        """Merge results with the same state, for all states"""
        for jobState in JobState._all():
            self.assertEquals(
                AggregateJobResults._aggregateState([
                    jobState,
                    jobState,
                ]),
                jobState
            )            
            
    def test_running(self):
        """Check that a job with any slave in the "running" state is marked as running"""
        self.assertEquals(
            AggregateJobResults._aggregateState([
                JobState.NEW,
                JobState.RUNNING,
                JobState.COMPLETE,
            ]),
            JobState.RUNNING
        )
    
    def test_unknown(self):
        """Check that a job with any slave in "unknown" state is unknown"""
        self.assertEquals(
            AggregateJobResults._aggregateState([
                JobState.NEW,
                JobState.RUNNING,
                JobState.COMPLETE,
                JobState.UNKNOWN,
            ]),
            JobState.UNKNOWN
        )     


class TestJobResults(DataObject):
    _attributes = {
        "job_state": JobState.RUNNING,
        "manual": 0,
        "add": 0,
        "average": 0,        
    }

class TestAggregateCalculations(AggregateJobResults):
    _attributes = {
        "job_state": JobState.RUNNING,
        "manual": 0,
        "add": 0,
        "average": 0,
    }
    _manuallyAggregate = ["manual"]
    _aggregateByAdding = ["add"]
    _aggregateByAveraging = ["average"]


class Calculations(AggregateJobResultsTestMixin, unittest.TestCase):
    def setUp(self):
        self.aggregateResults = TestAggregateCalculations()
    
    def test_add(self):
        """Check field adding in job results"""
        jobResults = [
            TestJobResults({ "add": 0 }),
            TestJobResults({ "add": 10 }),
            TestJobResults({ "add": 20 }),
        ]
        self.aggregateResults.aggregate(jobResults, 1, True)
        self.assertEquals(self.aggregateResults.add, 30)       
    
    def test_average(self):
        """Check field averaging in job results"""
        jobResults = [
            TestJobResults({ "average": 0 }),
            TestJobResults({ "average": 10 }),
            TestJobResults({ "average": 20 }),
        ]
        self.aggregateResults.aggregate(jobResults, 1, True)
        self.assertEquals(self.aggregateResults.average, 10.0)
    
    def test_manual(self):
        """Check that manually aggregated fields are skipped"""
        jobResults = [
            TestJobResults({ "manual": 5 }),
            TestJobResults({ "manual": 10 }),
            TestJobResults({ "manual": 20 }),
        ]
        self.aggregateResults.aggregate(jobResults, 1, True)
        self.assertEquals(self.aggregateResults.manual, self.aggregateResults._attributes["manual"])