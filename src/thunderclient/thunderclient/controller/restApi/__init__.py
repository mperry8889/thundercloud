from twisted.web import server
from twisted.web import resource

from status import StatusApiTree
from util import RootNode   

def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
    siteRoot.putChild("", RootNode())
    siteRoot.putChild("status", StatusApiTree)
    return server.Site(siteRoot)
