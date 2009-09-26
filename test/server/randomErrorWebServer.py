from twisted.internet import reactor
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web import server

import sys
import optparse


class NonRedirectingNode(Resource):
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
        509: "Bandwidth Limit Exceeded",
        510: "Not Extended",
    }
    
    def render_GET(self, request):
        responseCode = int(request.prepath[-1])
        request.setResponseCode(responseCode, self.httpCodes[responseCode])
        return "<html><body>%s</body></html>" % self.httpCodes[responseCode]
    
    render_POST = render_GET
    render_HEAD = render_GET


class RedirectingNode(Resource):
    httpCodes = {
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        306: "Switch Proxy",
        307: "Temporary Redirect",
    }
    
    def render_GET(self, request):
        responseCode = int(request.prepath[-1])
        request.setResponseCode(responseCode, self.httpCodes[responseCode])
        
        try:
            request.setHeader("Location", request.args["location"])
        except:
            request.setHeader("Location", "/200")
        
        request.finish()
    
    render_POST = render_GET
    render_HEAD = render_GET



if __name__ == "__main__":
    log.startLogging(sys.stderr)
    
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", type="int", dest="port", default=8080)
    (options, args) = parser.parse_args()
    
    root = Resource()
    nonRedirectingNode = NonRedirectingNode()
    for code in NonRedirectingNode.httpCodes.iterkeys():
        root.putChild("%s" % code, nonRedirectingNode)

    redirectingNode = RedirectingNode()
    for code in RedirectingNode.httpCodes.iterkeys():
        root.putChild("%s" % code, redirectingNode)
    
    site = server.Site(root)
    reactor.listenTCP(options.port, site)
    reactor.run()