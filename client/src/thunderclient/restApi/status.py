from nodes import RootNode
from nodes import LeafNode

class Root(RootNode):
    pass

class Threads(LeafNode):
    def render_GET(self, request):
        return "1 billion threads"
        
StatusApiTree = Root()
StatusApiTree.putChild("", Root())
StatusApiTree.putChild("threads", Threads())
