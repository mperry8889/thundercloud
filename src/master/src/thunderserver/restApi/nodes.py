from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from zope.interface import Interface, implements
import simplejson as json
import logging

from twisted.web.vhost import VHostMonsterResource

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
    
class Node(VHostMonsterResource):
    implements(INode)
    
    # there's a bit of indirection here having child nodes implement
    # POST and GET and not render_{POST,GET} -- but this is so that 
    # derived classes don't have to deal with the content-types, headers,
    # and etc
    
    # this differs from the nodes.py in the slave code in that requests here
    # will need to dump their own json, as these methods are just pass-through.
    # this is so job requests can return NOT_DONE_YET and return data on 
    # a callback so that the API doesn't just return True even if there's
    # an error somewhere along the way

    def render_GET(self, request):
        try:
            response = self.GET(request)
            if response != NOT_DONE_YET:
                request.setHeader("Content-Type", "text/plain")
            return response
        except Http400:
            request.setResponseCode(400)
        except Http404:
            request.setResponseCode(404)
        
    def render_POST(self, request):
        try:
            response = self.POST(request)
            if response != NOT_DONE_YET:
                request.setHeader("Content-Type", "text/plain")
            return response
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
    
    def writeJson(self, request, data):
        request.write(json.dumps(data))
        request.finish()

    
class RootNode(Node):
    isLeaf = False
   
class LeafNode(Node):
    isLeaf = True


