from thunderserver.orchestrator.slave import _SlaveAllocator
from thundercloud.spec.slave import SlaveSpec

from twisted.trial import unittest

class SlaveAllocator(_SlaveAllocator):
    def checkHealth(self):
        return True

class SingleSlave(unittest.TestCase):

    def setUp(self):
        self.sa = SlaveAllocator()


class MultiSlave(unittest.TestCase):
    
    def setUp(self):
        self.sa = SlaveAllocator()