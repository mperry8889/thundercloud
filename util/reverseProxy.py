
from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.web.resource import Resource

siteRoot = Resource()
site = server.Site(siteRoot)
port6000 = proxy.ReverseProxyResource('localhost', 6000, '')
port7000 = proxy.ReverseProxyResource('localhost', 7000, '')
port7001 = proxy.ReverseProxyResource('192.168.1.100', 7000, '')
port8000 = proxy.ReverseProxyResource('localhost', 8000, '')

siteRoot.putChild("master", port6000)
siteRoot.putChild("slave", port7000)
siteRoot.putChild("slave2", port7001)
siteRoot.putChild("ui", port8000)

reactor.listenTCP(8080, site)
reactor.run()
