from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from thundercloud.spec.job import JobSpec

from server.basicWebServer import BasicWebServer
from client.basicClient import BasicClient, runClient

from server.thundercloudSubProcesses import createMasterSubProcess, createSlaveSubProcess

from optparse import OptionParser
from multiprocessing import Process
import sys
import time
import signal
import os

if __name__ == "__main__":
    sys.path.insert(0, os.environ["PYTHONPATH"])
    
    parser = OptionParser()
    parser.add_option("-d", "--duration", type="int", dest="duration", default=5)
    parser.add_option("-f", "--function", type="string", dest="function", default="10")
    parser.add_option("-p", "--profile", type="int", dest="profile", default=0, help="0: hammer; 1: benchmark")
    parser.add_option("-s", "--slaves", type="int", dest="slaves", default=1)
    parser.add_option("-c", "--clients", type="int", dest="clients", default=1)
    (options, args) = parser.parse_args()
    options.url = "http://localhost:9996"

    print "Starting master"  
    masterProcess = createMasterSubProcess(9996)
    time.sleep(1)
    
    slaveProcesses = []
    for i in range(0, options.slaves):
        print "Starting slave %d" % i
        slaveProcess = createSlaveSubProcess(9997 + i, 9996)
        slaveProcesses.append(slaveProcess)
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    
    time.sleep(2)
    
    def quit(sig, frame):
        print "Received signal %s, quitting" % sig
        global masterProcess
        global slaveProcesses
        
        for process in [masterProcess] + slaveProcesses:
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
    
    #log.startLogging(sys.stdout)
    reactor.listenTCP(9995, BasicWebServer)
    reactor.callWhenRunning(runClient, options)
    reactor.run(installSignalHandlers=False)
    quit(signal.SIGINT, None)
    