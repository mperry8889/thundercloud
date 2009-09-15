# this is a crappy webserver, which returns a variety of error codes at random

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import server

from twisted.python import log

import random
import sys

random.seed()

class CrappyResource(Resource):
    
    httpCodes = {
        100: "Continue",
        102: "Processing",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        #300: "Multiple Choices",
        #301: "Moved Permanently",
        #302: "Found",
        #303: "See Other",
        #304: "Not Modified",
        #305: "Use Proxy",
        #306: "Switch Proxy",
        #307: "Temporary Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Request Entity Too Large",
        414: "Request-URI Too Long",
        415: "Unsupported Media Type",
        416: "Requested Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a Teapot",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        425: "Unordered Collection",
        426: "Upgrade Required",
        449: "Retry With",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        #509: "Bandwidth Limit Exceeded",
        510: "Not Extended",
    }
    
    def render(self, request):
        rand = random.randint(1, 100)
        
        # 35% chance of getting one of the codes above
        if rand >= 1 and rand < 35:
            key = random.choice(self.httpCodes.keys())
            log.msg("Sending HTTP %d %s" % (key, self.httpCodes[key]))
            request.setResponseCode(key, self.httpCodes[key])
            return self.httpCodes[key]
        
        # 10% chance of some kind of HTTP 300-level game
        #elif rand >= 35 and rand < 45:
        #    pass 
        
        # 5% chance of a timeout
        elif rand >= 45 and rand < 50:
            log.msg("Timing out request")
            return server.NOT_DONE_YET
        
        # 50% chance of returning a HTTP 200
        else:
            log.msg("Sending HTTP 200")
            return "1"


root = CrappyResource()
root.putChild("", CrappyResource())
RandomErrorWebServer = server.Site(root)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    reactor.listenTCP(9995, RandomErrorWebServer)
    reactor.run()