from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall

from thundercloud.spec.job import JobSpec, JobState, JobResults
from thundercloud.util.restApiClient import RestApiClient

import simplejson as json

import sys

class BasicClient(object):
    def __init__(self, url, jobSpec, callback=None, errback=None):
        self.url = url
        self.jobSpec = jobSpec
        self.task = None
        self.callback = callback
        self.errback = errback
    
    @inlineCallbacks
    def create(self):
        request = RestApiClient.POST(self.url + "/job",
                                     postdata = self.jobSpec.toJson())
        yield request

        print request.result
        self.jobId = json.loads(request.result)
        if self.jobId != False:
            self.jobId = int(self.jobId)
            returnValue(self.jobId)  
        else:
            raise Exception
    
    
    @inlineCallbacks
    def start(self):
        request = RestApiClient.POST(self.url + "/job/%d/start" % self.jobId)
        yield request        
        returnValue(request.result)
    
    
    @inlineCallbacks
    def poll(self, wait=1):
        if self.task is None:
            self.task = LoopingCall(self.poll)
            self.task.start(wait)

        else:                
            request = RestApiClient.GET(self.url + "/job/%d/state" % self.jobId)
            yield request
            
            if int(request.result) == JobState.COMPLETE:
                if self.callback is not None:
                    self.task.stop()
                    self.callback()
            elif int(request.result) == JobState.ERROR:
                if self.errback is not None:
                    self.task.stop()
                    self.errback()


    @inlineCallbacks
    def results(self, shortResults=False):
        request = RestApiClient.GET(self.url + "/job/%d/results?short=true" % self.jobId)
        yield request
        returnValue(JobResults(json.loads(request.result)))
