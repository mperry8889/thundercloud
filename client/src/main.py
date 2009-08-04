from twisted.internet import reactor
from thunderclient.restApi import createRestApi
import logging as log

log.basicConfig(level=log.DEBUG)

port = 7000
log.debug("Listening on port %s, starting reactor" % port)
reactor.listenTCP(port, createRestApi())

reactor.run()
