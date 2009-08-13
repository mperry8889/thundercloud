from twisted.web.resource import Resource
from zope.interface import Interface, implements
import simplejson as json

class Http400(Exception):
    pass

class Http404(Exception):
    pass

class INode(Interface):
    def GET(self, request):
        """GET operation"""
    
    def POST(self, request):
        """POST operation"""
    
class Node(Resource):
    implements(INode)
    
    # there's a bit of indirection here having child nodes implement
    # POST and GET and not render_{POST,GET} -- but this is so that 
    # derived classes don't have to deal with the content-types, headers,
    # and details of json output

    def render_GET(self, request):
        try:
            request.setHeader("Content-Type", "application/json")
            return json.dumps(self.GET(request))
        except Http400:
            request.setResponseCode(400)
        except Http404:
            request.setResponseCode(404)
        
    def render_POST(self, request):
        try:
            request.setHeader("Content-Type", "application/json")
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


