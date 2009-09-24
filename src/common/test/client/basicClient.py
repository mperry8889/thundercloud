from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall

from thundercloud.spec.job import JobSpec, JobState, JobResults
from thundercloud.util.restApiClient import RestApiClient

import simplejson as json

from optparse import OptionParser
import sys
import time
import signal
import os


class BasicClient(object):
    def __init__(self, url, jobSpec, username=None, password=None, callback=None, errback=None):
        self.url = url
        self.jobSpec = jobSpec
        self.task = None
        self.callback = callback
        self.errback = errback
        
        if username is None and password is None:
            self.credentials = None
        else:
            self.credentials = (username, password)
    
    @inlineCallbacks
    def create(self):
        request = RestApiClient.POST(self.url + "/job",
                                     postdata=self.jobSpec.toJson(),
                                     credentials=self.credentials)
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
        request = RestApiClient.POST(self.url + "/job/%d/start" % self.jobId,
                                     credentials=self.credentials)
        yield request        
        returnValue(request.result)
    
    
    @inlineCallbacks
    def poll(self, wait=1):
        if self.task is None:
            self.task = LoopingCall(self.poll)
            self.task.start(wait)

        else:          
            request = RestApiClient.GET(self.url + "/job/%d/state" % self.jobId,
                                        credentials=self.credentials)
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
        urlSuffix = ""
        if shortResults == True:
            urlSuffix += "?short=true"
            
        request = RestApiClient.GET(self.url + "/job/%d/results" % self.jobId + urlSuffix,
                                    credentials=self.credentials)
        yield request
        returnValue(JobResults(json.loads(request.result)))

@inlineCallbacks
def runClient(options):
    
    @inlineCallbacks
    def results():
        r = client.results()
        yield r
        print r.result
        print "Length of result is %.2fKB" % (len(str(r.result))/1024)
        reactor.stop()
    
    print "Running client"

    jobSpec = JobSpec()
    jobSpec.requests = {
        options.target: {
            "method": "GET",
            "postdata": None,
            "cookies": {},
        },
    }
    jobSpec.duration = options.duration
    jobSpec.transferLimit = 1024**3
    jobSpec.profile = options.profile
    jobSpec.clientFunction = options.function
    jobSpec.statsInterval = 1
    jobSpec.timeout = 10
    print jobSpec
    
    client = BasicClient(options.url, 
                         jobSpec, 
                         username=options.username, 
                         password=options.password, 
                         callback=results, 
                         errback=reactor.stop)
    try:
        r = client.create()
        yield r
        r = client.start()
        yield r
        r = client.poll()
        yield r 
    except:
        reactor.stop()


if __name__ == "__main__":
    sys.path.insert(0, os.environ["PYTHONPATH"])
    
    parser = OptionParser()
    parser.add_option("-u", "--url", type="string", dest="url", default="http://localhost:8080/api")
    parser.add_option("-d", "--duration", type="int", dest="duration", default=5)
    parser.add_option("-f", "--function", type="string", dest="function", default="10")
    parser.add_option("-p", "--profile", type="int", dest="profile", default=0, help="0: hammer; 1: benchmark")
    parser.add_option("-s", "--slaves", type="int", dest="slaves", default=1)
    parser.add_option("-c", "--clients", type="int", dest="clients", default=1)
    parser.add_option("-t", "--target", type="string", dest="target", default="http://localhost:8080/api")
    parser.add_option("--username", type="string", dest="username", default=None)
    parser.add_option("--password", type="string", dest="password", default=None)
    (options, args) = parser.parse_args()

    
    #log.startLogging(sys.stdout)
    reactor.callWhenRunning(runClient, options)
    reactor.run()
   