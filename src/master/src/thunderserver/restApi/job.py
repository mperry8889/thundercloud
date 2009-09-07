from zope.interface import Interface, implements
from twisted.web.server import NOT_DONE_YET
import jsonpickle
import simplejson as json
import logging

from nodes import RootNode
from nodes import LeafNode
from nodes import Http400, Http404

from ..orchestrator import Orchestrator
from thundercloud.job import IJob, JobSpec, JobResults

log = logging.getLogger("restApi.job")

# Handle requests sent to /job
class Job(RootNode):

    def GET(self, request):
       return "WORKING"

    def postCallback(self, jobId, request):
        self.putChild("%d" % jobId, JobNode())
        self.writeJson(request, jobId)

    # create a new job based on the given JSON job spec
    def POST(self, request):
        request.content.seek(0, 0)
        jobSpecObj = JobSpec(json.loads(request.content.read()))
        if not jobSpecObj.validate():
            raise Http400, "Invalid request"
        
        deferred = Orchestrator.createJob(jobSpecObj)
        deferred.addCallback(self.postCallback, request)
        return NOT_DONE_YET


# Handle requests for /job/n[/operation] URLs
class JobNode(LeafNode):
    implements(IJob)
    getCommands = ["results", "state"]
    postCommands = ["start", "pause", "resume", "stop", "modify", "remove"]
    
    # handle GET /job/n
    def GET(self, request):
        jobId = int(request.prepath[-1])
        if request.postpath and request.postpath[0].lower() in self.getCommands:
            return getattr(self, request.postpath[0].lower())(jobId, request)
        else:
            return self.results(jobId, None)

    # handle POST /job/n/operation -- call the appropriate method
    # for the given job ID
    def POST(self, request):
        if request.postpath and request.postpath[0].lower() in self.postCommands:
            jobId = int(request.prepath[-1])
            return getattr(self, request.postpath[0].lower())(jobId, request)
        else:
            raise Http400
    
    # start a new job
    def startCallback(self, value, request):
        self.writeJson(request, True)        
        
    def start(self, jobId, request):
        deferred = Orchestrator.startJob(jobId)
        deferred.addCallback(self.startCallback, request)
        return NOT_DONE_YET
    
    # pause an existing job
    def pauseCallback(self, value, request):
        self.writeJson(request, True)
        
    def pause(self, jobId, request):
        deferred = Orchestrator.pauseJob(jobId)
        deferred.addCallback(self.pauseCallback, request)
        return NOT_DONE_YET
    
    # resume an existing job
    def resumeCallback(self, value, request):
        self.writeJson(request, True)
        
    def resume(self, jobId, request):
        deferred = Orchestrator.resumeJob(jobId)
        deferred.addCallback(self.resumeCallback, request)
        return NOT_DONE_YET
            
    # stop an existing job
    def stopCallback(self, value, request):
        self.writeJson(request, True)
        
    def stop(self, jobId, request):
        deferred = Orchestrator.stopJob(jobId)
        deferred.addCallback(self.stopCallback, request)
        return NOT_DONE_YET
    
    # modify some properties of a running job
    def modify(self, jobId, args):
        pass
    # remove job from the system
    def remove(self, jobId, args):
        Orchestrator.removeJob(jobId)
        return True
    
    # status of a job in the system
    def stateCallback(self, value, request):
        self.writeJson(request, value)
        
    def state(self, jobId, request):
        short = None
        try:
            if request.args.has_key("short"):
                short = json.loads(request.args["short"][0])
        except AttributeError:
            pass
        deferred = Orchestrator.jobState(jobId)
        deferred.addCallback(self.stateCallback, request)
        return NOT_DONE_YET
    
    # get a job's statistics
    
    def resultsCallback(self, value, request):
        self.writeJson(request, value.toJson())
        
    def results(self, jobId, request):
        short = None
        try:
            if request.args.has_key("short"):
                short = json.loads(request.args["short"][0])
        except AttributeError:
            pass      
        
        deferred = Orchestrator.jobResults(jobId, short)
        deferred.addCallback(self.resultsCallback, request)
        return NOT_DONE_YET


# Build the API URL hierarchy
JobApiTree = Job()
JobApiTree.putChild("", Job())
