from twisted.web import resource

class RootNode(resource.Resource):
    isLeaf = False
    def render_GET(self, request):
        retVal = "dir listing (names):<br>"
        for item in self.listStaticNames():
            retVal += "%s<br>" % item
        return retVal