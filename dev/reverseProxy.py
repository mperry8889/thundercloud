
from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.web.resource import Resource

siteRoot = Resource()
site = server.Site(siteRoot)
port7000 = proxy.ReverseProxyResource('localhost', 7000, '')
port8000 = proxy.ReverseProxyResource('localhost', 8000, '')

siteRoot.putChild("api", port7000)
siteRoot.putChild("ui", port8000)

reactor.listenTCP(8080, site)
reactor.run()
