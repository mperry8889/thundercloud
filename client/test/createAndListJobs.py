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

#print "sleeping 3 seconds"
#time.sleep(3)
#print "POST /job/0/stop"
#client.request("POST", "/job/0/stop")
#print client.getresponse().read()
