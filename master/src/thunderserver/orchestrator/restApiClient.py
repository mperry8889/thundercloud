from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json

from thundercloud.job import IJob


class RestApiClient(object):
    implements(IJob)
    
    @classmethod
    def _request(cls, url, method, postdata=None, cookies=[], timeout=10):
        if postdata is not None:
            postdata = json.dumps(postdata)

        factory = HTTPClientFactory(url,
                             method=method,
                             postdata=postdata,
                             cookies=cookies, 
                             timeout=timeout)
        
        scheme, host, port, path = _parse(url)
        reactor.connectTCP(host, port, factory)
        return factory

    @classmethod    
    def POST(cls, url, postdata=None, cookies=[], timeout=10):
        request = cls._request(url, "POST", postdata, cookies, timeout)
        return request.deferred
    
    @classmethod    
    def GET(cls, url):
        request = cls._request(url, "GET")
        return request.deferred

    @classmethod    
    def start(cls, jobSpec):
        deferred = cls.POST("", postdata=jobSpec.toJson())
        deferred.addCallback()
        deferred.addErrback()
    
    @classmethod
    def pause(cls, jobId):
        pass
    
    @classmethod    
    def resume(cls, jobId):
        pass

    @classmethod    
    def stop(cls, jobId):
        pass