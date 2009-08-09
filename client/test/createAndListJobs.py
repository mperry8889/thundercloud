import httplib

client = httplib.HTTPConnection("localhost:7000")
print "GET /job"
client.request("GET", "/job")
print client.getresponse().read()

print "POST /job"
client.request("POST", "/job")
print client.getresponse().read()

print "GET /job/0"
client.request("GET", "/job/0")
print client.getresponse().read()

print "POST /job/0/start"
client.request("POST", "/job/0/start")
print client.getresponse().read()