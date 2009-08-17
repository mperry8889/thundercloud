from nodes import RootNode
from nodes import LeafNode

from ..orchestrator import Orchestrator

class HeartBeat(LeafNode):
    def GET(self, request):
        return True
    
class Jobs(LeafNode):
    def GET(self, request):
        return {"jobs": 0}
    

StatusApiTree = RootNode()
StatusApiTree.putChild("", RootNode())
StatusApiTree.putChild("heartbeat", HeartBeat())
StatusApiTree.putChild("jobs", Jobs())