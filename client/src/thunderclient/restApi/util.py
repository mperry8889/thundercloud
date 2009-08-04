from twisted.web import resource
import simplejson as json

class RootNode(resource.Resource):
    isLeaf = False
    def render_GET(self, request):
        # should be application/json
        request.setHeader("Content-Type", "text/plain")
        retVal = ""
        for item in self.listStaticNames():
            retVal += "%s\n" % item
        return retVal

class LeafNode(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        # should be application/json
        request.setHeader("Content-Type", "text/plain")
        retVal = ""
        for item in self.listStaticNames():
            retVal += "%s\n" % item
        return retVal