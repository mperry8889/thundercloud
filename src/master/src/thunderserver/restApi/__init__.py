from twisted.web import server, guard


from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource, guard
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm, Portal

from ..authentication.slave import SlaveRealm, SlaveDBChecker
from ..authentication.job import JobRealm, JobDBChecker
from ..db import dbConnection as db


from nodes import RootNode

class Die(RootNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()


## XXX this doesn't work
class HTTPAuthSessionWrapperFixed(guard.HTTPAuthSessionWrapper):
    def render(self, request):
        interface, avatar, aspect = self._portal.realm.requestAvatar("DBChecker", None, IResource)
        return avatar.render(request)


def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
#    siteRoot.putChild("", RootNode())
    siteRoot.putChild("die", Die()) # XXX

    # job tree needs its own authentication
    jobWrapper = HTTPAuthSessionWrapperFixed(Portal(JobRealm(), [JobDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud job management")])
    siteRoot.putChild("job", jobWrapper)

    # slave tree needs specific authentication
    slaveWrapper = HTTPAuthSessionWrapperFixed(Portal(SlaveRealm(), [SlaveDBChecker(db)]), [guard.BasicCredentialFactory("Slave Services")])
    siteRoot.putChild("slave", slaveWrapper)

    return server.Site(siteRoot)