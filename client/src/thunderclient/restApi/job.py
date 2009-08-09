from zope.interface import Interface, implements
import simplejson as json

from nodes import RootNode
from nodes import LeafNode
from nodes import Http400, Http404

from ..orchestrator import Orchestrator
from ..orchestrator.job import IJob, JobSpec
    

# Handle requests sent to /job
class Job(RootNode):
    
    # return some summary information about the list of
    # jobs in the system
    def GET(self, request):
        jobs = Orchestrator.listJobs()
        return [{id: "/job/%s" % id} for id in jobs]
    
    # create a new job based on the given JSON job spec
    def POST(self, request):
        jobId = Orchestrator.createJob(None)
        self.putChild("%d" % jobId, JobNode())
        return jobId


# Handle requests for /job/n[/operation] URLs
class JobNode(LeafNode):
    implements(IJob)
    
    # handle GET /job/n -- return a detailed status of the job
    def GET(self, request):
        return "status"
    
    # handle POST /job/n/operation -- call the appropriate method
    # for the given job ID
    def POST(self, request):
        if request.postpath:
            jobId = int(request.prepath[-1])
            return getattr(self, request.postpath[0])(jobId, request.args)
        else:
            raise Http400
     
    
    # start a new job
    def start(self, jobId, args):
        try:
            Orchestrator.startJob(jobId)
            return True
        except:
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
    def status(self, jobId, args):
        try:
            return Orchestrator.jobStatus(jobId)
        except:
            raise Http400


JobApiTree = Job()
JobApiTree.putChild("", Job())