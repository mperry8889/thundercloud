from twisted.web import server, guard

from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource, guard
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm, Portal

from thundercloud import config

from ..authentication.slave import SlaveDBChecker
from ..authentication.job import JobDBChecker
from ..restApi.job import JobRealm
from ..restApi.slave import SlaveRealm

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

    jobWrapper = guard.HTTPAuthSessionWrapper(Portal(JobRealm(), [JobDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud job management")])
    siteRoot.putChild("job", jobWrapper)
  
    # slave tree needs specific authentication
    slaveWrapper = guard.HTTPAuthSessionWrapper(Portal(SlaveRealm(), [SlaveDBChecker(db)]), [guard.BasicCredentialFactory("thundercloud slave management")])
    siteRoot.putChild("slave", slaveWrapper)

    return server.Site(siteRoot)