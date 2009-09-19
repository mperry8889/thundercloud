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
        return slaves
    
    def checkAllocationType(self, slaves, allocationType):
        if type(allocationType) != list:
            allocationType = [allocationType]
        
        for slave in slaves:
            self.failUnlessIn(slave.state, allocationType)
        return slaves


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


class SlaveAllocatorSlaveStates(SlaveAllocatorTestMixin, unittest.TestCase):
    """Allocation based on slave states"""
    
    def _updateSlaveStates(self, value):
        for i in range(1, 31):
            (slave, status, task) = self.sa._getSlaveById(i)
            if 1 <= i < 6:
                status.state = SlaveState.CONNECTED
            elif 6 <= i < 11:
                status.state = SlaveState.IDLE
            elif 11 <= i < 16:
                status.state = SlaveState.ALLOCATED            
            elif 16 <= i < 26:
                status.state = SlaveState.RUNNING
            elif 26 <= i < 31:
                status.state = SlaveState.DISCONNECTED    
 
    def setUp(self):
        self.sa = TestSlaveAllocator()
        
        # add 50 slaves, each can handle 1 request/sec.
        # states are as follows:
        # 5: connected, 5: idle, 5: allocated, 10: running, 5: disconnected
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

    def test_Idle(self):
        """Submit a job such that only the idle hosts will be allocated"""
        jobSpec = self.createJobSpec()
        jobSpec.clientFunction = "5"
        deferred = self.sa.allocate(jobSpec)
        deferred.addCallback(self.checkAllocationLength, 5)
        return deferred
    
    def test_IdlePlusAllocated(self):
        """Submit a job such that idle and previously allocated hosts will be allocated"""
        jobSpec = self.createJobSpec()
        jobSpec.clientFunction = "10"
        deferred = self.sa.allocate(jobSpec)
        deferred.addCallback(self.checkAllocationLength, 10)
        return deferred

    def test_IdlePlusAllocatedPlusRunning(self):
        """Submit a job that will take all idle, allocated, and running hosts"""
        jobSpec = self.createJobSpec()
        jobSpec.clientFunction = "20"
        deferred = self.sa.allocate(jobSpec)
        deferred.addCallback(self.checkAllocationLength, 20)
        return deferred

    def test_TooManyRequests(self):
        """Submit a job that wants more requests than the system can handle"""
        jobSpec = self.createJobSpec()
        jobSpec.clientFunction = "21"
        return self.failUnlessFailure(self.sa.allocate(jobSpec), InsufficientSlaveCapacity)
        
        


        