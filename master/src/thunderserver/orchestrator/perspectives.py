from twisted.internet.defer import Deferred, DeferredList

from restApiClient import RestApiClient



# Job perspective: local job ID corresponds to multiple remote job IDs on
# multiple slave servers
class JobPerspective(object):
    def __init__(self, jobId):
        self.jobId = jobId
        self.mapping = {}
    
    def addSlave(self, slave, remoteJobId):
        self.mapping[slave] = remoteJobId
    
    def removeSlave(self, slave):
        self.mapping.pop(slave)
    
    
    def start(self):
        return self._jobOp("startJob")

    def pause(self):
        return self._jobOp("pauseJob")
    
    def resume(self):
        return self._jobOp("resumeJob")
    
    def stop(self):
        return self._jobOp("stopJob")

    def _jobOpCallback(self, results, deferred):
        deferred.callback(results)
        
    def _jobOp(self, operation):
        deferred = Deferred()
        
        requests = []
        for slave in self.mapping.keys():
            requests.append(getattr(slave, "%s" % operation)(self.mapping[slave]))

        deferredList = DeferredList(requests)
        deferredList.addCallback(self._jobOpCallback, deferred)

        return deferred        


    def stateCallback(self, results, deferred):
        print "state results: %s" % results
        deferred.callback(results)
    
    def state(self):
        deferred = self._jobOp("jobState")
        deferred.addCallback(self.stateCallback, deferred)
        return deferred
    
    
    
    def resultsCallback(self, results, deferred):
        print "results results: %s" % results
        deferred.callback(results)
    
    def results(self, short):
        deferred = Deferred()
        
        requests = []
        for slave in self.mapping.keys():
            requests.append(slave.jobResults(self.mapping[slave], short))

        deferredList = DeferredList(requests)
        deferredList.addCallback(self.resultsCallback, deferred)

        return deferred   
        


# Slave perspective: send vanilla commands to slave servers
class SlavePerspective(object):
    def __init__(self, slaveSpec):
        self.slaveSpec = slaveSpec
        self.url = ""
    
    def createJob(self, jobSpec):
        return RestApiClient.POST(self.url+"/job", postdata=jobSpec.toJson())
           
    def startJob(self, jobId):
        return RestApiClient.POST(self.url+"/job/"+str(jobId)+"/start")

    def pauseJob(self, jobId):
        return RestApiClient.POST(self.url+"/job/"+str(jobId)+"/pause")
    
    def resumeJob(self, jobId):
        return RestApiClient.POST(self.url+"/job/"+str(jobId)+"/resume")
    
    def stopJob(self, jobId):
        return RestApiClient.POST(self.url+"/job/"+str(jobId)+"/stop")
    
    def jobState(self, jobId):
        return RestApiClient.GET(self.url+"/job/"+str(jobId)+"/state")
    
    def jobResults(self, jobId, short):
        url = self.url+"/job/"+str(jobId)+"/results"
        if short == True:
            url += "?short=true"
        return RestApiClient.GET(url) 
    
