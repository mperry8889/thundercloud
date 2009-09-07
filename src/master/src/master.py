from twisted.internet import reactor
from thunderserver.restApi import createRestApi
from thundercloud import constants
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

log.info("Listening on port %s, starting reactor" % constants.MASTER_PORT)
reactor.listenTCP(constants.MASTER_PORT, createRestApi())

reactor.run()
