from twisted.web import server
from twisted.web import resource

from status import StatusApiTree
from job import JobApiTree

from nodes import RootNode

def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
    siteRoot.putChild("", RootNode())
    siteRoot.putChild("status", StatusApiTree)
    siteRoot.putChild("job", JobApiTree)
    return server.Site(siteRoot)
