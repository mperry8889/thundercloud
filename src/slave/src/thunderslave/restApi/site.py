from status import StatusApiTree
from job import JobApiTree

from twisted.web.resource import Resource

from nodes import RootNode, LeafNode

class Die(LeafNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()
    
class Die2(Resource):
    isLeaf = True
    def render_GET(self, request):
        from twisted.internet import reactor
        reactor.stop()
    


#siteRoot = RootNode()
#siteRoot.putChild("", RootNode())
#siteRoot.putChild("status", StatusApiTree)
#siteRoot.putChild("job", JobApiTree)
#siteRoot.putChild("die", Die())

siteRoot = Resource()
siteRoot.isLeaf = False
siteRoot.putChild("", siteRoot)
siteRoot.putChild("die", Die2())