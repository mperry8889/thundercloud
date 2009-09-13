from twisted.web import server
from twisted.web import resource

from site import siteRoot

from thundercloud import config

from ..db import dbConnection as db

from ..authentication.root import RootRealm, RootDBChecker
from twisted.web import guard
from twisted.cred.portal import Portal

import logging

log = logging.getLogger("restApi")


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
    

