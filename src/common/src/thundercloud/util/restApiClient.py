from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json
import base64

import logging

log = logging.getLogger("restApiClient")

# Cython compatibility
def _RestApiClient__request(cls, url, method, postdata=None, cookies={}, timeout=None, credentials=None):

    extraHeaders = {}
    
    if postdata is not None:
        postdata = json.dumps(postdata)

    if credentials is not None:
        log.debug("adding creds")
        cred = "%s:%s" % (credentials[0], credentials[1])
        extraHeaders["Authorization"] = "Basic " + base64.encodestring(cred).replace('\012','')

   
    scheme, host, port, path = _parse(str(url))
       
    # replace multiple slashes in the url to a single slash
    # in the name of genericism this might be a bad idea but
    # whatever
    while "//" in path:
        path = path.replace("//", "/")
    if path[0] == "/":
        path = path[1:]

    url = str("%s://%s:%s/%s" % (scheme, host, port, path))
    log.debug("REST API Client request: %s %s" % (method, url))

    factory = HTTPClientFactory(url,
                         method=method,
                         postdata=postdata,
                         cookies=cookies, 
                         timeout=timeout,
                         headers=extraHeaders)

    
    reactor.connectTCP(host, port, factory)
    return factory

def _RestApiClient_POST(cls, url, postdata=None, cookies={}, timeout=None, credentials=None):
    request = cls._request(url, "POST", postdata, cookies, timeout, credentials)
    return request.deferred

def _RestApiClient_GET(cls, url, timeout=None, credentials=None):
    request = cls._request(url, "GET", credentials)
    return request.deferred


class RestApiClient(object):
    _request = classmethod(_RestApiClient__request)
    POST = classmethod(_RestApiClient_POST)
    GET = classmethod(_RestApiClient_GET)