from twisted.web.resource import Resource
from zope.interface import Interface, implements
import simplejson as json
import logging

log = logging.getLogger("restApi.node")

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
        request.setHeader("Content-Type", "text/plain")
        response = json.dumps(self.GET(request))
        return response
        
    def render_POST(self, request):
        request.setHeader("Content-Type", "text/plain")
        response = json.dumps(self.POST(request))
        return response
    
    def render_PUT(self, request):
        pass
    
    def GET(self, request):
        raise NotImplementedError
    
    def POST(self, request):
        raise NotImplementedError

    
class RootNode(Node):
    isLeaf = False
   
class LeafNode(Node):
    isLeaf = True


