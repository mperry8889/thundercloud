from twisted.internet import reactor
from thunderserver.restApi import createRestApi
from thundercloud import constants
import logging as log
#import psyco
#psyco.full()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % constants.MASTER_PORT)
reactor.listenTCP(constants.MASTER_PORT, createRestApi())

reactor.run()
