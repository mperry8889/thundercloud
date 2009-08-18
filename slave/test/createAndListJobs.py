import httplib
import time
import jsonpickle
import sys
import urllib

from thundercloud.job import JobSpec, JobResults

j = JobSpec()
j.requests = {
    "http://designerdogfood.com": {
        "method": "GET",
        "postdata": None,
        "cookies": [],
    },
}
j.duration = 120
j.transferLimit = float("inf")#5*1024*1024
j.statsGranularity = 10
j.profile = JobSpec.JobProfile.BENCHMARK

client = httplib.HTTPConnection("localhost:7000")

print "GET /job"
client.request("GET", "/job")
print client.getresponse().read()

p = jsonpickle.encode(j, unpicklable=False)
print "POST /job"
client.request("POST", "/job", p, {"Content-type": "application/json"})
id = client.getresponse().read()
print id

print "GET /job/%s" % id
client.request("GET", "/job/%s" % id)
print client.getresponse().read()

print "POST /job/%s/start" % id
client.request("POST", "/job/%s/start" % id)
print client.getresponse().read()

print "sleeping 5 seconds"
time.sleep(5)
print "POST /job/0/pause"
client.request("POST", "/job/0/pause")
print client.getresponse().read()

print "sleeping 2 seconds"
time.sleep(2)
print "POST /job/0/resume"
client.request("POST", "/job/0/resume")
print client.getresponse().read()

print "GET /job/active"
client.request("GET", "/job/active")
print client.getresponse().read()

print "sleeping %s sec" % j.duration
time.sleep(j.duration)

print "GET /job/%s/results" % id
client.request("GET", "/job/%s/results" % id)
results = client.getresponse().read()
print results
obj = jsonpickle.decode(jsonpickle.decode(results))
print obj


#print "sleeping 60 seconds"
#time.sleep(60)
#print "POST /job/%s/stop" % id
#client.request("POST", "/job/%s/stop" % id)
#print client.getresponse().read()

#print "GET /job/complete"
#client.request("GET", "/job/complete")
#print client.getresponse().read()

#print "POST /job/%s/remove" % id
#client.request("POST", "/job/%s/remove" % id)
#print client.getresponse().read()

#print "GET /job/complete"
#client.request("GET", "/job/complete")
#print client.getresponse().read()

#print "sleeping 90 seconds"
#time.sleep(90)
#print "GET /die"
#client.request("GET", "/die")
