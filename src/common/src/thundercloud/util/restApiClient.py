from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json

import logging

log = logging.getLogger("restApiClient")

# Cython compatibility
def _RestApiClient__request(cls, url, method, postdata=None, cookies={}, timeout=10):
    if postdata is not None:
        postdata = json.dumps(postdata)
    
    scheme, host, port, path = _parse(str(url))
       
    # replace multiple slashes in the url to a single slash
    # in the name of genericism this might be a bad idea but
    # whatever
    while "//" in path:
        path = path.replace("//", "/")
    if path[0] == "/":
        path = path[1:]

    url = str("%s://%s:%s/%s" % (scheme, host, port, path))

    log.debug("REST API Request: (%s) %s" % (method, url))
    factory = HTTPClientFactory(url,
                         method=method,
                         postdata=postdata,
                         cookies=cookies, 
                         timeout=timeout)
    
    reactor.connectTCP(host, port, factory)
    return factory

def _RestApiClient_POST(cls, url, postdata=None, cookies={}, timeout=10):
    request = cls._request(url, "POST", postdata, cookies, timeout)
    return request.deferred

def _RestApiClient_GET(cls, url):
    request = cls._request(url, "GET")
    return request.deferred


class RestApiClient(object):
    _request = classmethod(_RestApiClient__request)
    POST = classmethod(_RestApiClient_POST)
    GET = classmethod(_RestApiClient_GET)