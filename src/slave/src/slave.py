from twisted.internet import reactor
from thunderslave.restApi import createRestApi
from thundercloud import config
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % config.SLAVE_PORT)
reactor.listenTCP(config.SLAVE_PORT, createRestApi())

reactor.run()
