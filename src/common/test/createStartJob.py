# this is just a simple script to create and run a job

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet.defer import inlineCallbacks

from thundercloud.spec.job import JobSpec
from thundercloud.util.restApiClient import RestApiClient

from server.basicWebServer import BasicWebServer

tc = "http://localhost:6001"
requested_hits = 100

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


reactor.listenTCP(9995, BasicWebServer)
reactor.callWhenRunning(createJob)
reactor.run()
