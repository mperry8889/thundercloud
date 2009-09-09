from twisted.internet.defer import Deferred, DeferredList

from thundercloud.spec.job import JobResults, JobState

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


def AggregateJobResults_aggregateStatisticsByTimeSort(cls, a, b):
    return int(float(a)-float(b))


def AggregateJobResults_aggregateStatisticsByTime(cls, statsList, statsInterval):
    result = {}
    for stat in statsList:
        sortedKeys = sorted(stat.keys(), AggregateJobResults._aggregateStatisticsByTimeSort)
        for i in range(0, int(float(sortedKeys[-1]))+1, statsInterval):
            try:
                result[i]
            except KeyError:
                result[i] = {}
                    
            for k in sortedKeys:
                if i - statsInterval <= float(k) < i + statsInterval:
                    distance = (statsInterval - abs(float(k) - i))
                    weight = distance / statsInterval
                    for v in ["requestsCompleted", "requestsFailed", "requestsPerSec", "clients", "iterations"]:
                        try:
                            result[i][v] += stat[k][v] * weight
                        except KeyError:
                            result[i][v] = stat[k][v] * weight

                    try:
                        result[i]["averageResponseTime"] += stat[k]["averageResponseTime"]
                    except KeyError:
                        result[i]["averageResponseTime"] = 0

    return result


class AggregateJobResults(JobResults):

    # Cython compatibility for static methods
    _merge = classmethod(AggregateJobResults_merge)
    _aggregateState = classmethod(AggregateJobResults_aggregateState)
    _aggregateStatisticsByTimeSort = classmethod(AggregateJobResults_aggregateStatisticsByTimeSort)
    _aggregateStatisticsByTime = classmethod(AggregateJobResults_aggregateStatisticsByTime)   
    
    _manuallyAggregate = ["jobId", "state", "statisticsByTime"]
    _aggregateByAdding = ["iterations", "requestsCompleted", "requestsFailed", "bytesTransferred", "errors", "nodes"]
    _aggregateByAveraging = ["elapsedTime", "transferLimit", "duration", "timeout"]
    
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
        self.elapsedTime = jobResults[0].elapsedTime
        
        # aggregate the job state separately    
        self.state = AggregateJobResults._aggregateState([jobResult.state for jobResult in jobResults])
        
        # statisticsByTime might not exist if the results are shortResults. if it's there, aggregate some results
        if shortResults != True:
            self.statisticsByTime = AggregateJobResults._aggregateStatisticsByTime([jobResult.statisticsByTime for jobResult in jobResults], statsInterval)
        
        
# Job perspective: local job ID corresponds to multiple remote job IDs on
# multiple slave servers
class JobPerspective(object):
    def __init__(self, jobId, jobSpec):
        self.jobId = jobId
        self.jobSpec = jobSpec
        self.mapping = {}
    
    def addSlave(self, slave, remoteJobId):
        self.mapping[slave] = remoteJobId
    
    def removeSlave(self, slave):
        self.mapping.pop(slave)

    # shortcut methods
    def _jobOpCallback(self, results, deferred):
        deferred.callback(results)
    
    def _jobOp(self, operation):
        deferred = Deferred()
        
        requests = []
        for slave, remoteId in self.mapping.iteritems():
            requests.append(getattr(slave, "%s" % operation)(remoteId))

        deferredList = DeferredList(requests)
        deferredList.addCallback(self._jobOpCallback, deferred)

        return deferred

    
    def start(self):
        return self._jobOp("startJob")

    def pause(self):
        return self._jobOp("pauseJob")
    
    def resume(self):
        return self._jobOp("resumeJob")
    
    def stop(self):
        return self._jobOp("stopJob")


    def stateCallback(self, results, deferred):
        states = []
        for (result, state) in results:
            states.append(result)
        deferred.callback(AggregateJobResults._aggregateState(states))
    
    def state(self):
        deferred = self._jobOp("jobState")
        deferred.addCallback(self.stateCallback, deferred)
        return deferred


    def resultsCallback(self, results, deferred, shortResults):
        aggregateResults = AggregateJobResults()
        
        # decode all json.  for speed's sake, try once as a list comprehension, but if one is
        # false then the list comprehension will fail -- fall back to a for loop,
        # rejecting failed responses
        decodedResults = []
        try:
            decodedResults = [(status, JobResults(json.loads(result))) for (status, result) in results]
        except:
            log.debug("Could not decode results. results: %s" % results)
       
            for (status, result) in results:
                if status == True:
                    decodedResults.append((status, JobResults(json.loads(result))))
           
        # set the job ID to the master's job ID
        aggregateResults.jobId = self.jobId
        
        # combine and add results from all the slave servers.  this 
        # aggregates things like bytes transferred, requests completed, etc.
        aggregateResults.aggregate([result for (status, result) in decodedResults], self.jobSpec.statsInterval, shortResults)
        
        # if we're doing no stats, cut out statisticsByTime complete
        if shortResults == True:
            try:
                del(aggregateResults.statisticsByTime)
            except AttributeError:
                pass     
        
        deferred.callback(aggregateResults)
    
    def results(self, shortResults):
        deferred = Deferred()
        
        requests = []
        for slave in self.mapping.keys():
            requests.append(slave.jobResults(self.mapping[slave], shortResults))

        deferredList = DeferredList(requests)
        deferredList.addCallback(self.resultsCallback, deferred, shortResults)

        return deferred
