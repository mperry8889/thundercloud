from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python import log

from thundercloud.spec.job import JobSpec

from server.basicWebServer import BasicWebServer
from client.basicClient import BasicClient

from server.thundercloudSubProcesses import createMasterSubProcess, createSlaveSubProcess

from multiprocessing import Process
import sys
import time
import signal
import os

@inlineCallbacks
def runClient():
    
    @inlineCallbacks
    def results():
        r = client.results()
        yield r
        print r.result
        reactor.stop()
    
    print "Running client"
    global duration

    jobSpec = JobSpec()
    jobSpec.requests = {
        "http://localhost:9995/": {
            "method": "GET",
            "postdata": None,
            "cookies": {},
        },
    }
    jobSpec.duration = duration
    jobSpec.transferLimit = 1024**3
    jobSpec.profile = JobSpec.JobProfile.HAMMER
    jobSpec.clientFunction = 100/jobSpec.duration
    jobSpec.statsInterval = 1
    jobSpec.timeout = 10
    
    client = BasicClient("http://localhost:9996", jobSpec, callback=results, errback=reactor.stop)
    r = client.create()
    yield r
    r = client.start()
    yield r
    r = client.poll()
    yield r 
    

if __name__ == "__main__":
    sys.path.insert(0, os.environ["PYTHONPATH"])
    
    if len(sys.argv) >= 2:
        duration = int(sys.argv[1])
    else:
        duration = 5
    
    print "Starting master"  
    masterProcess = createMasterSubProcess(9996)
    time.sleep(5)
    
    print "Starting slave"
    slaveProcess = createSlaveSubProcess(9997, 9996)
    time.sleep(5)
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    
    def quit(sig, frame):
        print "Received signal %s, quitting" % sig
        global masterProcess
        global slaveProcess
        
        for process in [masterProcess, slaveProcess]:
            process.terminate()
        
        try:
            reactor.stop()
        except:
            pass
            
            # twisted will probably need 2 SIGINTs to stop
            #os.kill(process.pid, sig)
            #os.kill(process.pid, sig)
            
            #while process.is_alive():
            #    process.terminate()
            #    time.sleep(0.2)
    
        #sys.exit(1)
    
    log.startLogging(sys.stdout)
    reactor.listenTCP(9995, BasicWebServer)
    reactor.callWhenRunning(runClient)
    reactor.run(installSignalHandlers=False)
    quit(signal.SIGINT, None)
    