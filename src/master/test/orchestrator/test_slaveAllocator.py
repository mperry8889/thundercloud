from thunderserver.orchestrator.slave import _SlaveAllocator
from thundercloud.spec.slave import SlaveSpec

from twisted.trial import unittest

class SingleSlave(unittest.TestCase):

    def setUp(self):
        self.sa = _SlaveAllocator()


class MultiSlave(unittest.TestCase):
    
    def setUp(self):
        self.sa = _SlaveAllocator()