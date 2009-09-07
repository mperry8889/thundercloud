from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json

from thundercloud.job import IJob

import logging

log = logging.getLogger("orchestrator.restApiClient")

# Cython compatibility
def RestApiClient__request(cls, url, method, postdata=None, cookies={}, timeout=10):
    if postdata is not None:
        postdata = json.dumps(postdata)

    log.debug("REST API Request: (%s) %s" % (method, url))
    factory = HTTPClientFactory(str(url),
                         method=method,
                         postdata=postdata,
                         cookies=cookies, 
                         timeout=timeout)
    
    scheme, host, port, path = _parse(str(url))
    reactor.connectTCP(host, port, factory)
    return factory

def RestApiClient_POST(cls, url, postdata=None, cookies={}, timeout=10):
    request = cls._request(url, "POST", postdata, cookies, timeout)
    return request.deferred

def RestApiClient_GET(cls, url):
    request = cls._request(url, "GET")
    return request.deferred


class RestApiClient(object):
    implements(IJob)

    _request = classmethod(RestApiClient__request)
    POST = classmethod(RestApiClient_POST)
    GET = classmethod(RestApiClient_GET)