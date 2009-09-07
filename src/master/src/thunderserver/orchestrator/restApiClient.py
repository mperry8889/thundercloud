from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json

from thundercloud.job import IJob

import logging

log = logging.getLogger("orchestrator.restApiClient")


class RestApiClient(object):
    implements(IJob)
    
    @classmethod
    def _request(cls, url, method, postdata=None, cookies={}, timeout=10):
        if postdata is not None:
            postdata = json.dumps(postdata)

        #log.debug("Requesting %s on %s" % (method, url))
        factory = HTTPClientFactory(str(url),
                             method=method,
                             postdata=postdata,
                             cookies=cookies, 
                             timeout=timeout)
        
        scheme, host, port, path = _parse(str(url))
        reactor.connectTCP(host, port, factory)
        return factory

    @classmethod    
    def POST(cls, url, postdata=None, cookies={}, timeout=10):
        request = cls._request(url, "POST", postdata, cookies, timeout)
        return request.deferred
    
    @classmethod    
    def GET(cls, url):
        request = cls._request(url, "GET")
        return request.deferred
