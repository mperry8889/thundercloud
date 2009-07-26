from twisted.web import client
from twisted.internet import reactor
from twisted.python.util import println
from twisted.web.error import Error
from twisted.internet import threads
import sys
from time import sleep

#from thunderclient.controller.restApi import createRestApi

from Queue import Queue

#reactor.listenTCP(7000, createRestApi())
#reactor.run()

max_concurrent = 10
active = 0
requests = 1
completed_requests = 0

def callbackToQueue(v, q, i):
    global completed_requests
    global active
    global max_concurrent
    
    try:
        completed_requests = completed_requests + 1
    except Exception, e:
        raise
    
    println("finished request %d, len=%d" % (i, len(v)))
    active = active-1

    if completed_requests == requests:
        println("ok, done")
        #reactor.stop()
        return
    
    while active < max_concurrent:
        println("adding new workers")
        popQ(q)

def errorHandler(v, q):
    global completed_requests
    global active
    global max_concurrent
    
    completed_requests = completed_requests + 1
    popQ(q)
    println("aborted, %s" % v)
    sleep(5)

def popQ(q):       
    global completed_requests
    global active
    global max_concurrent
    
    active = active + 1
    println("popping queue, qlen=%d active=%d max_concurrent=%d completed_requests=%d" % (q.qsize(),active,max_concurrent,completed_requests))
    
    if q.empty():
        println("queue is empty")
        return
    
    try:
        i = q.get()        
        d = client.getPage("http://192.168.1.100/", timeout=5)
        d.addCallback(callbackToQueue, q, i)
        d.addErrback(errorHandler, q)
    except:
        println("caught exception, stopping")
    #    reactor.stop()

q = Queue()
for i in range(1, requests+1):
    q.put(i)

while active < max_concurrent:
    popQ(q)

reactor.run()
println("exiting")
sys.exit()
