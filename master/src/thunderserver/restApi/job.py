from zope.interface import Interface, implements
import jsonpickle
import simplejson as json
import logging

from nodes import RootNode
from nodes import LeafNode

from thundercloud.job import IJob, JobSpec, JobResults

log = logging.getLogger("restApi.job")

# Handle requests sent to /job
class Job(RootNode):    
    # return some summary information about the list of
    # jobs in the system
    def GET(self, request):
        jobs = Controller.listJobs()
        return [{id: "/job/%s" % id} for id in jobs]
    
    # create a new job based on the given JSON job spec
    def POST(self, request):
        request.content.seek(0, 0)
        jobSpecObj = JobSpec(json.loads(request.content.read()))
        if not jobSpecObj.validate():
            raise Http400, "Invalid request"
        
        jobId = Controller.createJob(jobSpecObj)
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
        pass
    
    # pause an existing job
    def pause(self, jobId, args):
        pass
    
    # resume an existing job
    def resume(self, jobId, args):
        pass
            
    # stop a running job
    def stop(self, jobId, args):
        pass
    
    # modify some properties of a running job
    def modify(self, jobId, args):
        pass
    
    # status of a job in the system
    def state(self, jobId, args):
        pass

    # remove job from the system
    def remove(self, jobId, args):
        pass
    
    # get a job's statistics
    def results(self, jobId, args):
        pass


# Build the API URL hierarchy
JobApiTree = Job()
JobApiTree.putChild("", Job())