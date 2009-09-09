from twisted.internet import reactor
from thunderserver.restApi import createRestApi
from thundercloud import config
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % config.MASTER_PORT)
reactor.listenTCP(config.MASTER_PORT, createRestApi())

reactor.run()
