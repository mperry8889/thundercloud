from twisted.web import server
from twisted.web import resource
from twisted.internet import reactor

from nodes import RootNode
from job import JobApiTree

class Die(RootNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()

def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
    siteRoot.putChild("", RootNode())
    siteRoot.putChild("job", JobApiTree)
    siteRoot.putChild("die", Die()) # XXX
    return server.Site(siteRoot)