from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import server
from twisted.python import log

import sys

class BasicResource(Resource):
    isLeaf = False
    def render_GET(self, request):
        return "1"


root = BasicResource()
root.putChild("", BasicResource())
BasicWebServer = server.Site(root)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    reactor.listenTCP(9995, BasicWebServer)
    reactor.run()