from twisted.web import server
from twisted.web import resource

from status import StatusApiTree
from command import CommandApiTree

from nodes import RootNode

def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
    siteRoot.putChild("", RootNode())
    siteRoot.putChild("status", StatusApiTree)
    siteRoot.putChild("command", CommandApiTree)
    return server.Site(siteRoot)
