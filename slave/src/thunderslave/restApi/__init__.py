from twisted.web import server
from twisted.web import resource

from status import StatusApiTree
from job import JobApiTree

from nodes import RootNode

class Die(RootNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()

def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
    siteRoot.putChild("", RootNode())
    siteRoot.putChild("status", StatusApiTree)
    siteRoot.putChild("job", JobApiTree)
    siteRoot.putChild("die", Die()) # XXX
    return server.Site(siteRoot)
