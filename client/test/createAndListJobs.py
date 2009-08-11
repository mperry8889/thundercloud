import httplib
import time

client = httplib.HTTPConnection("localhost:7000")
print "GET /job"
client.request("GET", "/job")
print client.getresponse().read()

print "POST /job"
client.request("POST", "/job")
id = client.getresponse().read()
print id

print "GET /job/%s" % id
client.request("GET", "/job/%s" % id)
print client.getresponse().read()

print "POST /job/%s/start" % id
client.request("POST", "/job/%s/start" % id)
print client.getresponse().read()

#print "sleeping 5 seconds"
#time.sleep(5)
#print "POST /job/0/pause"
#client.request("POST", "/job/0/pause")
#print client.getresponse().read()

#print "sleeping 2 seconds"
#time.sleep(2)
#print "POST /job/0/resume"
#client.request("POST", "/job/0/resume")
#print client.getresponse().read()

print "GET /job/active"
client.request("GET", "/job/active")
print client.getresponse().read()

print "sleeping 3 seconds"
time.sleep(3)
print "POST /job/%s/stop" % id
client.request("POST", "/job/%s/stop" % id)
print client.getresponse().read()

print "GET /job/complete"
client.request("GET", "/job/complete")
print client.getresponse().read()

print "POST /job/%s/remove" % id
client.request("POST", "/job/%s/remove" % id)
print client.getresponse().read()

print "GET /job/complete"
client.request("GET", "/job/complete")
print client.getresponse().read()