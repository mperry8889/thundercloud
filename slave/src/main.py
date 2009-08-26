from twisted.internet import reactor
from thunderslave.restApi import createRestApi
import logging
#import psyco
#psyco.full()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

port = 7000
log.debug("Listening on port %s, starting reactor" % port)
reactor.listenTCP(port, createRestApi())

reactor.run()
