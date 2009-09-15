from thunderserver.orchestrator.job import AggregateJobResults
from thundercloud.spec.job import JobState

from twisted.trial import unittest

class AJR(unittest.TestCase):
    
    def setUp(self):
        self.aggregateResults = AggregateJobResults()
            
    def test_singleShortResult(self):
        """Test a single short result, no merge necessary"""
    
    def test_singleLongResult(self):
        """Test a single long result, no merge necessary"""
    
    def test_mergeMultipleShortResults(self):
        """Merge 3 short results"""
    
    def test_mergeMultipleLongResults(self):
        """Merge 3 long results"""
    
    def test_mergeMixedStates(self):
        """Merge several results with mixed status codes"""
    
        # if all states are the same, the aggregate should obviously
        # be the same
        for jobState in JobState._all():
            self.assertEquals(
                AggregateJobResults._aggregateState([
                    jobState,
                    jobState,
                ]),
                jobState            
            )
    
        # if any slave is still running, the whole job is still running
        self.assertEquals(
            AggregateJobResults._aggregateState([
                JobState.NEW,
                JobState.RUNNING,
                JobState.COMPLETE,
            ]),
            JobState.RUNNING
        )

        # if one state is unknown, the whole job is unknown
        self.assertEquals(
            AggregateJobResults._aggregateState([
                JobState.NEW,
                JobState.RUNNING,
                JobState.COMPLETE,
                JobState.UNKNOWN,
            ]),
            JobState.UNKNOWN
        )        

    
    def test_mergeSlaveDropoff(self):
        """Merge results with a slave drop-off, leading to a lack of status from a slave during some time period"""
    
    def test_mergeMixedElapsedTime(self):
        """Check that wildly varying elapsed times are handled correctly"""
    
