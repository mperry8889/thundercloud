from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from thunderslave.restApi import createRestApi
from thundercloud import config
from thundercloud.util.restApiClient import RestApiClient
from thundercloud.spec.slave import SlaveSpec
import simplejson as json
import logging
import sys
import socket

from twisted.python import log as twistedLog


@inlineCallbacks
def startServer(port):
    logging.basicConfig(level=eval("logging.%s" % config.parameter("log", "level")))
    log = logging.getLogger("main")
       
    if config.parameter("misc", "standalone", type=bool) != True:
        # connect to master server in INI file
        scheme = config.parameter("master", "scheme")
        host = config.parameter("master", "host")
        port = config.parameter("master", "port", type=int)
        path = config.parameter("master", "path")
        
        slaveSpec = SlaveSpec()
        slaveSpec.host = socket.gethostname()
        slaveSpec.port = config.parameter("network", "port", type=int)
        slaveSpec.path = ""
        
        masterUrl = "%s://%s:%d/%s/slave" % (scheme, host, port, path)
        
        log.info("Connecting to master: %s" % masterUrl)
        
        try:
            request = RestApiClient.POST(str(masterUrl), slaveSpec.toJson(), timeout=10, credentials=("foo", "foo"))
            yield request
        except:
            log.error("Could not connect to master.  Exiting")
            reactor.stop()
            return
        
        slaveId = int(request.result)
        log.info("Connected to master.  This server is slave ID %d" % slaveId)
    
    reactor.listenTCP(config.parameter("network", "port", type=int), createRestApi())
    log.debug("Listening on port %s, starting reactor" % config.parameter("network", "port"))
    #twistedLog.startLogging(sys.stderr)

if __name__ == "__main__":
    try:
        config.readConfig(sys.argv[1])
    except:
        print "No config file specified, exiting"
        sys.exit(1)
    
    reactor.callWhenRunning(startServer, config.parameter("network", "port", type=int))
    reactor.run()
