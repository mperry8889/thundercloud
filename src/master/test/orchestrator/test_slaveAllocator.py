from thunderserver.orchestrator.slave import _SlaveAllocator
from thundercloud.spec.slave import SlaveSpec, SlaveState
from thundercloud.spec.job import JobSpec

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.internet.defer import DeferredList, Deferred, inlineCallbacks, returnValue

# subclass the slave allocator so health checks always return True,
# since there won't be any live servers here
class TestSlaveAllocator(_SlaveAllocator):
    def checkHealth(self, slave):
        deferred = Deferred()
        reactor.callLater(0, deferred.callback, True)
        return deferred
    
class SlaveAllocatorTestMixin(object):
    def setUp(self, slaves=10, maxRequestsPerSec=10):
        self.sa = TestSlaveAllocator()
        
        # add 10 slaves
        deferredList = []
        for i in range(0, slaves):
            slaveSpec = SlaveSpec()
            slaveSpec.host = "localhost"
            slaveSpec.port = i
            slaveSpec.path = "/"
            slaveSpec.maxRequestsPerSec = maxRequestsPerSec
            deferred = self.sa.addSlave(slaveSpec)
            deferredList.append(deferred)

        return DeferredList(deferredList)    

    def tearDown(self):
        slavesToRemove = []
        for slaveId, (slave, status, task) in self.sa.slaves.iteritems():
            slavesToRemove.append(slaveId)
        
        [self.sa.removeSlave(slaveId) for slaveId in slavesToRemove]

    def createJobSpec(self):
        jobSpec = JobSpec()
        jobSpec.profile = JobSpec.JobProfile.HAMMER
        jobSpec.requests = { "http://localhost:80/foo": { "method": "GET", "postdata": None, "cookies": {}} }
        jobSpec.duration = 60
        jobSpec.transferLimit = 1024**3
        jobSpec.statsInterval = 1
        jobSpec.timeout = 10
        jobSpec.clientFunction = "100"
        return jobSpec


class SlaveAllocatorInternalMethods(SlaveAllocatorTestMixin, unittest.TestCase):
    def test_Filters(self):
        """Test internal filters"""
        for (slaveId, (slave, status, task)) in self.sa.slaves.iteritems():
            self.assertEquals((slave, status, task), self.sa._getSlaveById(slaveId))
            self.assertEquals((slave, status, task), self.sa._getSlaveByObject(slave))
            self.assertEquals((slave, status, task), self.sa._getSlaveBySlaveSpec(slave.slaveSpec))
        
        self.assertEquals(self.sa.slaves.values(), self.sa._getSlavesInState(SlaveState.IDLE))        
        return True


class SlaveAllocatorLowerBounds(SlaveAllocatorTestMixin, unittest.TestCase): 
    def setUp(self):
        self.sa = TestSlaveAllocator()
        
        # add 50 slaves, each can handle 1 request/sec
        deferredList = []
        for i in range(0, 50):
            slaveSpec = SlaveSpec()
            slaveSpec.host = "localhost"
            slaveSpec.port = i
            slaveSpec.path = "/"
            slaveSpec.maxRequestsPerSec = 1
            deferred = self.sa.addSlave(slaveSpec)
            deferredList.append(deferred)

        return DeferredList(deferredList)

    def test_SlaveAllocatorLowerBounds(self):
        """Slave allocator lower bounds.
        Each slave can do 1 request/sec, so each allocation requiring 1 <= i <= 50
        requests/sec should allocate i slaves""
        
        def checkAllocationLength(slaves, length):
                self.assertNotEquals(slaves, [])
                self.assertEquals(len(slaves), length)
        
        deferredList = []
        
        for i in range(1, 51):
            jobSpec = self.createJobSpec()
            jobSpec.clientFunction = "%d" % i            
            deferred =  self.sa.allocate(jobSpec)
            deferred.addCallback(checkAllocationLength, i)
            deferredList.append(deferred)
            
        return DeferredList(deferredList)