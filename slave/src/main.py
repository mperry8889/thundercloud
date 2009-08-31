from twisted.internet import reactor
from thunderslave.restApi import createRestApi
from thundercloud import constants
import logging
#import psyco
#psyco.full()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % constants.SLAVE_PORT)
reactor.listenTCP(constants.SLAVE_PORT, createRestApi())

reactor.run()
