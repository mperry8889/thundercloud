from twisted.internet import reactor
from thunderclient.controller.restApi import createRestApi

reactor.listenTCP(7000, createRestApi())
reactor.run()
