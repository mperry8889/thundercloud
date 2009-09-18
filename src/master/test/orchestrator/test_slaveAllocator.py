from thunderserver.orchestrator.slave import _SlaveAllocator, InsufficientSlaveCapacity
from thundercloud.spec.slave import SlaveSpec, SlaveState
from thundercloud.spec.job import JobSpec

from thunderserver.db import dbConnection as db

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
        db.execute("UPDATE slaveno SET slaveNo = 1")

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

    def checkAllocationLength(self, slaves, length):
            self.assertNotEquals(slaves, [])
            self.assertEquals(len(slaves), length)


class SlaveAllocatorInternalMethods(SlaveAllocatorTestMixin, unittest.TestCase):
    def test_Filters(self):
        """Internal slave getByX methods"""
        for (slaveId, (slave, status, task)) in self.sa.slaves.iteritems():
            self.assertEquals((slave, status, task), self.sa._getSlaveById(slaveId))
            self.assertEquals((slave, status, task), self.sa._getSlaveByObject(slave))
            self.assertEquals((slave, status, task), self.sa._getSlaveBySlaveSpec(slave.slaveSpec))
        
        self.assertEquals(self.sa.slaves.values(), self.sa._getSlavesInState(SlaveState.IDLE))        
        return True


class SlaveAllocatorBounds(SlaveAllocatorTestMixin, unittest.TestCase): 
    """Allocation boundary checks.  Slave capacity threshold is disabled."""
    
    def setUp(self):
        self.sa = TestSlaveAllocator()
        
        # add 10 slaves, each can handle 1 request/sec
        deferredList = []
        for i in range(0, 10):
            slaveSpec = SlaveSpec()
            slaveSpec.host = "localhost"
            slaveSpec.port = i
            slaveSpec.path = "/"
            slaveSpec.maxRequestsPerSec = 1
            deferred = self.sa.addSlave(slaveSpec)
            deferredList.append(deferred)

        return DeferredList(deferredList)

    def test_LowerBounds(self):
        """Lower bounds of slave allocation: test for minimum amount of request/sec per slave"""
        deferredList = []
        
        for i in range(1, 11):
            jobSpec = self.createJobSpec()
            jobSpec.clientFunction = "%d" % i            
            deferred =  self.sa.allocate(jobSpec)
            deferred.addCallback(self.checkAllocationLength, i)
            deferredList.append(deferred)
            
        return DeferredList(deferredList)
    
    
    def test_OverAllocation(self):
        """Overallocate each slave.  Allocation should fail due to insufficient capacity"""
        jobSpec = self.createJobSpec()
        jobSpec.clientFunction = "%d" % 11
        return self.failUnlessFailure(self.sa.allocate(jobSpec), InsufficientSlaveCapacity)


class SlaveAllocatorSlaveStates(SlaveAllocatorTestMixin, unittest.TestCase):
    """Allocation based on slave states"""
    
    def _updateSlaveStates(self, value):
        print sorted(self.sa.slaves.keys())
        for i in range(1, 6):
            (slave, status, task) = self.sa._getSlaveById(i)
            status.state = SlaveState.CONNECTED
        
        for j in range(6, 16):
            (slave, status, task) = self.sa._getSlaveById(j)
            status.state = SlaveState.IDLE

        for k in range(16, 26):
            (slave, status, task) = self.sa._getSlaveById(k)
            status.state = SlaveState.RUNNING
        
        for l in range(26, 31):
            (slave, status, task) = self.sa._getSlaveById(l)
            status.state = SlaveState.DISCONNECTED    
        return True                   
        
    def setUp(self):
        self.sa = TestSlaveAllocator()
        
        # add 50 slaves, each can handle 1 request/sec.
        # states are as follows:
        # 5: connected, 10: idle, 10: running, 5: disconnected
        deferreds = []
        for i in range(0, 30):
            slaveSpec = SlaveSpec()
            slaveSpec.host = "localhost"
            slaveSpec.port = i
            slaveSpec.path = "/"
            slaveSpec.maxRequestsPerSec = 1
            deferred = self.sa.addSlave(slaveSpec)
            deferreds.append(deferred)

        deferredList = DeferredList(deferreds)
        deferredList.addCallback(self._updateSlaveStates)
        return deferredList

    def test_Foo(self):
        """Foo"""
        return True
    

        