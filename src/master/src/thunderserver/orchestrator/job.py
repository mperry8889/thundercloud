from thundercloud.spec.job import JobResults, JobState

from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

from slave import SlaveAllocator

import simplejson as json

import logging

log = logging.getLogger("orchestrator.perspectives")

def _mergeDict(lhs, rhs, merge=lambda l, r: l):
    if type(lhs) != type(rhs) != dict:
        raise AttributeError

    if lhs == {}:
        return dict(rhs)
    
    if rhs == {}:
        return dict(lhs)
    
    result = dict(lhs)
    for k, v in rhs.iteritems():
        if lhs.has_key(k):
            result[k] = merge(lhs[k], rhs[k])
        else:
            result[k] = v
    
    return result


# Cython compatibility
def AggregateJobResults_merge(cls, lhs, rhs):
    if type(lhs) == type(rhs) == dict:
        if sorted(lhs.keys()) == sorted(rhs.keys()):
            result = {}
            for k in result.iterkeys():
                result[k] = lhs[k] + rhs[k]
            return result
        else:
            return _mergeDict(lhs, rhs)
    else:
        return lhs + rhs

 
def AggregateJobResults_aggregateState(cls, states):
    # just get unique states
    stateSet = list(set(states))
    
    # if all states are the same, return it. this
    # should be the usual case, since we wait for
    # all jobs to change state before returning a value
    if len(stateSet) == 1:
        return stateSet[0]
    
    # if any slave job is unknown, the whole thing is unknown
    if JobState.UNKNOWN in stateSet:
        return JobState.UNKNOWN
    
    # if any slave job is still running, the entire job is still running
    if JobState.RUNNING in stateSet:
        return JobState.RUNNING


def AggregateJobResults_aggregateResultsByTimeSort(cls, a, b):
    return int(float(a)-float(b))


def AggregateJobResults_aggregateResultsByTime(cls, statsList, statsInterval):
    result = {}
    for stat in statsList:
        sortedKeys = sorted(stat.keys(), AggregateJobResults._aggregateResultsByTimeSort)
        for i in range(0, int(float(sortedKeys[-1]))+1, statsInterval):
            try:
                result[i]
            except KeyError:
                result[i] = {}
                    
            for k in sortedKeys:
                if i - statsInterval <= float(k) < i + statsInterval:
                    distance = (statsInterval - abs(float(k) - i))
                    weight = distance / statsInterval
                    for v in ["iterations_total", "iterations_success", "iterations_fail", "requestsPerSec"]:
                        try:
                            result[i][v] += stat[k][v] * weight
                        except KeyError:
                            result[i][v] = stat[k][v] * weight

                    # XXX this is summing when it really should be averaging
                    for u in ["timeToConnect", "timeToFirstByte", "responseTime"]:
                        try:
                            result[i][u] += stat[k][u]
                        except KeyError:
                            result[i][u] = 0
                        

    # go through and change float values to reduced precision values
    # hopefully this shitty use of CPU time saves some network time and bandwidth
    for key in result.keys():
        if type(result[key]) == dict:
            for subkey in result[key].keys():
                if type(result[key][subkey]) == float:
                    result[key][subkey] = "%.3f" % result[key][subkey]

    return result


class AggregateJobResults(JobResults):

    # Cython compatibility for static methods
    _merge = classmethod(AggregateJobResults_merge)
    _aggregateState = classmethod(AggregateJobResults_aggregateState)
    _aggregateResultsByTimeSort = classmethod(AggregateJobResults_aggregateResultsByTimeSort)
    _aggregateResultsByTime = classmethod(AggregateJobResults_aggregateResultsByTime)   
    
    _manuallyAggregate = ["job_id", "job_state", "results_byTime"]
    _aggregateByAdding = ["job_nodes", "iterations_total", "iterations_complete", "iterations_fail", "transfer_total",  "results_errors"]
    _aggregateByAveraging = ["time_elapsed", "time_paused", "limits_transfer", "limits_duration"]
    
    def aggregate(self, jobResults, statsInterval, shortResults):
        for attr in self._attributes:                
            # don't change the job ID, since we want the job ID in the
            # master server and not the slave servers
            if attr in self._manuallyAggregate:
                continue
        
            # XXX
            if attr in self._aggregateByAveraging:
                setattr(self, attr, getattr(jobResults[0], attr))
        
            if attr in self._aggregateByAdding:           
                for jobResult in jobResults:
                    # if we're using a default value and the job result has something
                    # legit, just use it
                    if getattr(self, attr) == self._attributes[attr]:
                        setattr(self, attr, getattr(jobResult, attr))
                        continue

                    # otherwise selectively do stuff by type
                    elif type(getattr(self, attr)) == dict:
                        setattr(self, attr, _mergeDict(getattr(self, attr), getattr(jobResult, attr), AggregateJobResults._merge))
                    elif type(getattr(self, attr)) == int:
                        setattr(self, attr, getattr(self, attr) + getattr(jobResult, attr))
                    elif type(getattr(self, attr)) == float:
                        setattr(self, attr, getattr(self, attr) + getattr(jobResult, attr))
        
        # elapsed time
        self.time_elapsed = jobResults[0].time_elapsed
        
        # aggregate the job state separately    
        self.job_state = AggregateJobResults._aggregateState([jobResult.job_state for jobResult in jobResults])
        
        # results_byTime might not exist if the results are shortResults. if it's there, aggregate some results
        if shortResults != True:
            self.results_byTime = AggregateJobResults._aggregateResultsByTime([jobResult.results_byTime for jobResult in jobResults], statsInterval)
        
        
# Job perspective: local job ID corresponds to multiple remote job IDs on
# multiple slave servers
class JobHealthError(Exception):
    pass

class JobHealth(object):
    OK = 0
    ERROR = 1

class JobPerspective(object):
    def __init__(self, jobId, jobSpec):
        self.jobId = jobId
        self.jobSpec = jobSpec
        self.mapping = {}
        self.health = JobHealth.OK
    
    def addSlave(self, slave, remoteJobId):
        self.mapping[slave] = remoteJobId
    
    def removeSlave(self, slave):
        self.mapping.pop(slave)
    
    @inlineCallbacks
    def handleSlaveError(self, slave, error):
        # XXX should handle different errors differently
        # for now we'll just assume the slave gets killed off
        
        log.error("Job health compromised: lost a slave server")
        self.health = JobHealth.ERROR
        
        log.warn("Removing slave %s://%s:%d/%s" % (slave.slaveSpec.scheme, slave.slaveSpec.host, slave.slaveSpec.port, slave.slaveSpec.path))
        self.removeSlave(slave)
        SlaveAllocator.degrade(slave)

        # we should probably mark the job state as unknown and cancel
        # the whole thing, since it couldn't be completed as asked
        yield self._jobOp("stopJob", ignoreHealth=True)
        returnValue(True)
   
    # this is just a pass-through to the DeferredList callback
    def _jobOpSlaveCallback(self, value):
        return value
    
    # though here we want to intercept errors
    def _jobOpSlaveErrback(self, error, slave):
        self.handleSlaveError(slave, error)
        return error
   
    @inlineCallbacks
    def _jobOp(self, operation, *args, **kwargs):
        try:
            if kwargs["ignoreHealth"] == True:
                pass
            else:
                raise            
        except:
            if self.health == JobHealth.ERROR:
                returnValue(False)

        requests = []
        for slave, remoteId in self.mapping.iteritems():
            request = getattr(slave, "%s" % operation)(remoteId, *args)
            request.addCallback(self._jobOpSlaveCallback)
            request.addErrback(self._jobOpSlaveErrback, slave)
            requests.append(request)

        deferredList = DeferredList(requests, consumeErrors=True)
        yield deferredList
        
        returnValue(deferredList.result)
    
    def start(self):
        return self._jobOp("startJob")

    def pause(self):
        return self._jobOp("pauseJob")
    
    def resume(self):
        return self._jobOp("resumeJob")
    
    def stop(self):
        return self._jobOp("stopJob")
    
    @inlineCallbacks
    def state(self):
        
        # this line is repeated twice: once at the beginning for
        # new calls to state(), and once after checking the DeferredList
        # in case the health has suffered during the call
        if self.health == JobHealth.ERROR:
            returnValue(JobState.ERROR)
            
        request = self._jobOp("jobState")
        yield request

        # see above
        if self.health == JobHealth.ERROR:
            returnValue(JobState.ERROR)

        states = []
        for (result, state) in request.result:
            if result == True:
                states.append(int(json.loads(state)))
        returnValue(AggregateJobResults._aggregateState(states))
        
  
    @inlineCallbacks
    def results(self, shortResults):
        request = self._jobOp("jobResults", shortResults)
        yield request
        
        if self.health == JobHealth.ERROR:
            returnValue(False)
        
        results = request.result
        aggregateResults = AggregateJobResults()
        
        # decode all json.  for speed's sake, try once as a list comprehension, but if one is
        # false then the list comprehension will fail -- fall back to a for loop,
        # rejecting failed responses
        decodedResults = []
        try:
            decodedResults = \
                [(status, JobResults(json.loads(result))) for (status, result) in results]
        except:
            log.debug("Could not decode all results. results: %s" % results)
       
            for (status, result) in results:
                if status == True:
                    decodedResults.append((status, JobResults(json.loads(result))))
           
        # set the job ID to the master's job ID
        aggregateResults.job_id = self.jobId
        
        # combine and add results from all the slave servers.  this 
        # aggregates things like bytes transferred, requests completed, etc.
        aggregateResults.aggregate([result for (status, result) in decodedResults], self.jobSpec.statsInterval, shortResults)
        
        # if we're doing no stats, cut out results_byTime complete
        if shortResults == True:
            try:
                del(aggregateResults.results_byTime)
            except AttributeError:
                pass
        
        # if the job is unhealthy, stop the whole thing, and overwrite whatever the
        # merged state was
        if self.health == JobHealth.ERROR:
            aggregateResults.job_state = JobState.ERROR
        
        returnValue(aggregateResults)       
        
