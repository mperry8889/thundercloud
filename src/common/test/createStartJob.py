import unittest

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet.defer import inlineCallbacks

from thundercloud.spec.job import JobSpec
from thundercloud.util.restApiClient import RestApiClient

tc = "http://localhost:6001"
requested_hits = 50

class BasicResource(Resource):
    isLeaf = False
    counter = 0
    def render_GET(self, request):
        self.counter += 1
        print "received hit %d..." % self.counter
        if self.counter == requested_hits:
            print "quitting..."
            reactor.callLater(1, reactor.stop)
        return "1"


@inlineCallbacks
def createJob():
    jobSpec = JobSpec()
    jobSpec.requests = {
        "http://localhost:9995/": {
            "method": "GET",
            "postdata": None,
            "cookies": {},
        },
    }
    jobSpec.duration = 5
    jobSpec.transferLimit = 1024**3
    jobSpec.profile = JobSpec.JobProfile.HAMMER
    jobSpec.clientFunction = requested_hits/jobSpec.duration
    jobSpec.statsInterval = 1
    jobSpec.timeout = 10
    
    request = RestApiClient.POST(tc + "/job",
                               postdata = jobSpec.toJson())
    yield request

    jobId = int(request.result)
    print "Created job %d" % jobId
    print "Starting job..."
    
    request = RestApiClient.POST(tc + "/job/%d/start" % jobId)
    yield request
    
    if request.result == True:
        print "Job started"


    
root = BasicResource()
root.putChild("", BasicResource())
reactor.listenTCP(9995, server.Site(root))
reactor.callWhenRunning(createJob)
reactor.run()
