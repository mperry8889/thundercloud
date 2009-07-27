from twisted.web import resource

from util import RootNode

class Root(RootNode):
    pass

class Threads(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "1 billion threads"
        
StatusApiTree = Root()
StatusApiTree.putChild("", Root())
StatusApiTree.putChild("threads", Threads())
