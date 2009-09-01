from zope.interface import implements
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet import reactor

import simplejson as json

from thundercloud.job import IJob


class RestApiClient(object):
    implements(IJob)
    
    @classmethod
    def _request(self, url, method, postdata=None, cookies=[], timeout=10):
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
    def POST(self, url, postdata=None, cookies=[], timeout=10):
        request = self._request(url, "POST", postdata, cookies, timeout)
        return request.deferred
    
    @classmethod    
    def GET(self, url):
        request = self._request(url, "GET")
        return request.deferred

    @classmethod    
    def start(self, jobSpec):
        deferred = self.POST("", postdata=jobSpec.toJson())
        deferred.addCallback()
        deferred.addErrback()
    
    @classmethod
    def pause(self, jobId):
        pass
    
    @classmethod    
    def resume(self, jobId):
        pass

    @classmethod    
    def stop(self, jobId):
        pass