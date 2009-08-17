from twisted.internet import reactor
from thunderslave.restApi import createRestApi
import logging as log
#import psyco
#psyco.full()

log.basicConfig(level=log.DEBUG)

port = 7000
log.debug("Listening on port %s, starting reactor" % port)
reactor.listenTCP(port, createRestApi())

reactor.run()
