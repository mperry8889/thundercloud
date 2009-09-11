
from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.web.resource import Resource


class AppendingReverseProxyResource(proxy.ReverseProxyResource):
    
    def __init__(self, host, port, prefix, postfix, reactor=reactor):
        super(AppendingReverseProxyResource, self).__init__(self, host, port, prefix, reactor=reactor)
        self.path += postfix
    

siteRoot = Resource()
site = server.Site(siteRoot)
port6001 = proxy.ReverseProxyResource('localhost', 6001, '')
port7000 = proxy.ReverseProxyResource('localhost', 7000, '')
port8000 = proxy.ReverseProxyResource('localhost', 8000, '')

siteRoot.putChild("ui", port8000)
siteRoot.putChild("slave", port7000)
siteRoot.putChild("api", port6001)

reactor.listenTCP(8080, site)
reactor.run()
