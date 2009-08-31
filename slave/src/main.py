from twisted.internet import reactor
from thunderslave.restApi import createRestApi
from thundercloud import constants
import logging
#import psyco
#psyco.full()
#import cProfile

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % constants.SLAVE_PORT)
reactor.listenTCP(constants.SLAVE_PORT, createRestApi())

#cProfile.run("reactor.run()", filename="profile-stats", sort=1)
reactor.run()
