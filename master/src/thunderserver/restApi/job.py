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
            return getattr(self, request.postpath[0].lower())(jobId, request.args)
        else:
            return self.results(jobId, None)

    # handle POST /job/n/operation -- call the appropriate method
    # for the given job ID
    def POST(self, request):
        if request.postpath and request.postpath[0].lower() in self.postCommands:
            jobId = int(request.prepath[-1])
            return getattr(self, request.postpath[0].lower())(jobId, request.args)
        else:
            raise Http400
    
    # start a new job
    def start(self, jobId, args):
        Orchestrator.startJob(jobId)
        return True
    
    # pause an existing job
    def pause(self, jobId, args):
        Orchestrator.pauseJob(jobId)
        return True
    
    # resume an existing job
    def resume(self, jobId, args):
        Orchestrator.resumeJob(jobId)
        return True
            
    # stop a running job
    def stop(self, jobId, args):
        Orchestrator.stopJob(jobId)
        return True
    
    # modify some properties of a running job
    def modify(self, jobId, args):
        pass
    
    # status of a job in the system
    def state(self, jobId, args):
        return Orchestrator.jobState(jobId)

    # remove job from the system
    def remove(self, jobId, args):
        Orchestrator.removeJob(jobId)
        return True
    
    # get a job's statistics
    def results(self, jobId, args):
        short = None
        try:
            if args.has_key("short"):
                short = json.loads(args["short"][0])
        except AttributeError:
            pass            
            
        return Orchestrator.jobResults(jobId, short).toJson()


# Build the API URL hierarchy
JobApiTree = Job()
JobApiTree.putChild("", Job())