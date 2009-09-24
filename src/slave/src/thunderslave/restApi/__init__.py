from zope.interface import implements
from twisted.web import server
from twisted.web import resource

from status import StatusApiTree
from job import JobApiTree

from twisted.web.resource import Resource

from nodes import RootNode, LeafNode

from thundercloud import config

from ..authentication.root import RootDBChecker
from twisted.web import guard
from twisted.cred.portal import Portal
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm


import logging

log = logging.getLogger("restApi")

class Die(LeafNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()

class RootRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, siteRoot, lambda: None
        raise NotImplementedError()


def createRestApi():
    try:
        if config.parameter("network", "authentication", type=bool) == False:
            log.warn("HTTP Authentication disabled")
            return server.Site(siteRoot)
        else:
            raise
    except:
        rootWrapper = guard.HTTPAuthSessionWrapper(Portal(RootRealm(), [RootDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud root management")])
        return server.Site(rootWrapper)
    

siteRoot = RootNode()
siteRoot.putChild("", RootNode())
siteRoot.putChild("status", StatusApiTree)
siteRoot.putChild("job", JobApiTree)
siteRoot.putChild("die", Die())
