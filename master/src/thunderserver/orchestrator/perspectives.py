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
        map(lambda s: s.startJob(self.mapping[s]), self.mapping.keys())
        return True

    def pause(self):
        map(lambda s: s.pauseJob(self.jobId), self.mapping.keys())
        return True
    
    def resume(self):
        map(lambda s: s.resumeJob(self.jobId), self.mapping.keys())
        return True
    
    def stop(self):
        map(lambda s: s.stopJob(self.jobId), self.mapping.keys())
        return True

    def state(self):
        map(lambda s: s.jobState(self.jobId), self.mapping.keys())
    
    def results(self, args):
        map(lambda s: s.jobResults(self.jobId), self.mapping.keys())


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
    
    def jobResults(self, jobId, args):
        return RestApiClient.GET(self.url+"/job/"+str(jobId)+"/results") 
    
