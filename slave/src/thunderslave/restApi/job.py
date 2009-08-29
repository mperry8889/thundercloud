from zope.interface import Interface, implements
import jsonpickle
import simplejson as json
import logging

from nodes import RootNode
from nodes import LeafNode
from nodes import Http400, Http404

from ..orchestrator import Orchestrator
from thundercloud.job import IJob, JobSpec, JobResults

log = logging.getLogger("restApi.job")

# List only active jobs, /job/active
class ActiveJobs(RootNode):
    def GET(self, request):
        jobs = Orchestrator.listActiveJobs()
        return [{id: "/job/%s" % id} for id in jobs]

# List only inactive jobs, /job/inactive
class CompleteJobs(RootNode):
    def GET(self, request):
        jobs = Orchestrator.listCompleteJobs()
        return [{id: "/job/%s" % id} for id in jobs]


# Handle requests sent to /job
class Job(RootNode):    
    # return some summary information about the list of
    # jobs in the system
    def GET(self, request):
        jobs = Orchestrator.listJobs()
        return [{id: "/job/%s" % id} for id in jobs]
    
    # create a new job based on the given JSON job spec
    def POST(self, request):
        request.content.seek(0, 0)
        jobSpecObj = JobSpec(json.loads(request.content.read()))
        if not jobSpecObj.validate():
            raise Http400, "Invalid request"
        
        jobId = Orchestrator.createJob(jobSpecObj)
        self.putChild("%d" % jobId, JobNode())
        return jobId


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
        try:
            Orchestrator.startJob(jobId)
            return True
        except Exception, e:
            print e
            raise Http400
    
    # pause an existing jo
    def pause(self, jobId, args):
        try:
            Orchestrator.pauseJob(jobId)
            return True
        except:
            raise Http400
    
    # resume an existing job
    def resume(self, jobId, args):
        try:
            Orchestrator.resumeJob(jobId)
            return True
        except:
            raise Http400
            
    # stop a running job
    def stop(self, jobId, args):
        try:
            Orchestrator.stopJob(jobId)
            return True
        except:
            raise Http400
    
    # modify some properties of a running job
    def modify(self, jobId, args):
        pass
    
    # status of a job in the system
    def state(self, jobId, args):
        try:
            return Orchestrator.jobState(jobId)
        except:
            raise Http400

    # remove job from the system
    def remove(self, jobId, args):
        try:
            Orchestrator.removeJob(jobId)
            return True
        except:
            raise Http400
    
    # get a job's statistics
    def results(self, jobId, args):
        short = None
        try:
            if args.has_key("short"):
                short = json.loads(args["short"][0])
        except AttributeError:
            pass            
            
        try:
            return Orchestrator.jobResults(jobId, short).toJson()
        except:
            raise Http400

JobApiTree = Job()
JobApiTree.putChild("", Job())
JobApiTree.putChild("active", ActiveJobs())
JobApiTree.putChild("complete", CompleteJobs())