from twisted.web import server, guard

from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource, guard
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm, Portal

from thundercloud import config

from ..authentication.slave import SlaveRealm, SlaveDBChecker
from ..authentication.job import JobRealm, JobDBChecker
from ..db import dbConnection as db

from job import Job
from slave import Slave

from nodes import RootNode

import logging

log = logging.getLogger("restApi")


# XXX need to remove
class Die(RootNode):
    def GET(self, request):
        from twisted.internet import reactor
        reactor.stop()


def createRestApi():
    """Create the REST API URL hierarchy"""
    siteRoot = RootNode()
#    siteRoot.putChild("", RootNode())
    siteRoot.putChild("die", Die()) # XXX

    # job tree needs its own authentication, unless authentication is disabled
    try:
        if config.parameter("network", "authentication", type=bool) == False:
            log.warn("HTTP Authentication disabled for /job")
            siteRoot.putChild("job", Job())
        else:
            raise
    except:
        jobWrapper = guard.HTTPAuthSessionWrapper(Portal(JobRealm(), [JobDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud job management")])
        siteRoot.putChild("job", jobWrapper)


    # slave tree needs specific authentication
    try:
        if config.parameter("network", "authentication", type=bool) == False:
            log.warn("HTTP Authentication disabled for /slave")
            siteRoot.putChild("slave", Slave())
        else:
            raise
    except:
        slaveWrapper = guard.HTTPAuthSessionWrapper(Portal(SlaveRealm(), [SlaveDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud slave management")])
        siteRoot.putChild("slave", slaveWrapper)

    return server.Site(siteRoot)