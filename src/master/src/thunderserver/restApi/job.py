from zope.interface import Interface, implements
from twisted.web.server import NOT_DONE_YET
import simplejson as json
import logging

from twisted.web import guard
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm, Portal

from thunderserver.authentication.job import JobNodeDBChecker

from ..db import dbConnection as db

from nodes import RootNode
from nodes import LeafNode
from nodes import Http400

from ..orchestrator import Orchestrator
from thundercloud.spec.job import IJob, JobSpec

log = logging.getLogger("restApi.job")


# HTTP authentication realm for /job.  All users can access this
class JobRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, Job, lambda: None
        raise NotImplementedError()

# HTTP authentication realm for /job/n.  Only the user who created the job
# can access this -- that way, user 1 can't manipulate user 2's jobs, and so forth.
class JobNodeRealm(object):
    implements(IRealm)
 
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, JobNode(), lambda: None
        raise NotImplementedError()


# Handle requests sent to /job.  JobRealm should always hand out the same instance, so
# this is more-or-less a singleton.  Otherwise every new job would be added as a child to
# a new instance of Job(), and in turn none of them could be accessed properly.
class _Job(RootNode):
    def postCallback(self, jobId, request):
        jobNodeWrapper = guard.HTTPAuthSessionWrapper(Portal(JobNodeRealm(), [JobNodeDBChecker(db, jobId)]), [guard.BasicCredentialFactory("thundercloud job #%d" % jobId)])
        self.putChild("%d" % jobId, jobNodeWrapper)
        self.writeJson(request, jobId)
    
    def postErrback(self, error, request):
        log.debug("Job POST failed: %s" % error)
        self.writeJson(request, False)

    # create a new job based on the given JSON job spec
    def POST(self, request):
        request.content.seek(0, 0)
        jobSpecObj = JobSpec(json.loads(request.content.read()))
        if not jobSpecObj.validate():
            raise Http400, "Invalid request"
        
        log.debug("Creating job, user: %s" % request.getUser())
        deferred = Orchestrator.createJob(request.getUser(), jobSpecObj)
        deferred.addCallback(self.postCallback, request)
        deferred.addErrback(self.postErrback, request)
        return NOT_DONE_YET
Job = _Job()

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
    
    # status of a job in the system
    def stateCallback(self, value, request):
        self.writeJson(request, value)
        
    def state(self, jobId, request):
        deferred = Orchestrator.jobState(jobId)
        deferred.addCallback(self.stateCallback, request)
        return NOT_DONE_YET
    
    # get a job's results
    def resultsCallback(self, value, request):
        self.writeJson(request, value.toJson())
        
    def results(self, jobId, request):
        shortResults = None
        try:
            if request.args.has_key("short"):
                shortResults = json.loads(request.args["short"][0])
        except AttributeError:
            pass      
        
        deferred = Orchestrator.jobResults(jobId, shortResults)
        deferred.addCallback(self.resultsCallback, request)
        return NOT_DONE_YET
