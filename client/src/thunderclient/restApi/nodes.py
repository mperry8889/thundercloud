from twisted.web.resource import Resource
from zope.interface import Interface, implements
import simplejson as json

class Http400(Exception):
    pass

class Http404(Exception):
    pass

class INode(Interface):
    def GET(self, request):
        pass
    
    def POST(self, request):
        pass
    
class Node(Resource):
    implements(INode)

    def render_GET(self, request):
        try:
            request.setHeader("Content-Type", "text/plain")
            return json.dumps(self.GET(request))
        except Http400:
            request.setResponseCode(400)
        except Http404:
            request.setResponseCode(404)
        
    def render_POST(self, request):
        try:
            request.setHeader("Content-Type", "text/plain")
            return json.dumps(self.POST(request))
        except Http400:
            request.setResponseCode(400)
        except Http404:
            request.setResponseCode(404)
    
    def render_PUT(self, request):
        pass
    
    def GET(self, request):
        return None
    
    def POST(self, request):
        return None

    
class RootNode(Node):
    isLeaf = False
   
class LeafNode(Node):
    isLeaf = True


