from twisted.internet import reactor
from thunderslave.restApi import createRestApi
from thundercloud import config
from thundercloud.util.restApiClient import RestApiClient
from thundercloud.spec.slave import SlaveSpec
import simplejson as json
import logging
import sys
import socket

def registerMasterCallback(value):
    log.info("Connected to master.  This server is slave ID %d" % int(value))

def registerMasterErrback(value):
    log.error("Unable to register with master")
    log.error("%s" % value)
    reactor.stop()

try:
    config.readConfig(sys.argv[1])
except:
    print "No config file specified, exiting"
    sys.exit(1)

logging.basicConfig(level=eval("logging.%s" % config.parameter("log", "level")))
log = logging.getLogger("main")

# connect to master server in INI file
scheme = config.parameter("master", "scheme")
host = config.parameter("master", "host")
port = config.parameter("master", "port", type=int)
path = config.parameter("master", "path")

if config.parameter("misc", "standalone", type=bool) != True:
    slaveSpec = SlaveSpec()
    slaveSpec.host = socket.gethostname()
    slaveSpec.port = config.parameter("network", "port", type=int)
    slaveSpec.path = ""
    
    masterUrl = "%s://%s:%d/%s/slave" % (scheme, host, port, path)
    
    log.info("Connecting to master: %s" % masterUrl)
    
    d = RestApiClient.POST(str(masterUrl), slaveSpec.toJson(), timeout=10)
    d.addCallback(registerMasterCallback)
    d.addErrback(registerMasterErrback)


reactor.listenTCP(config.parameter("network", "port", type=int), createRestApi())
log.debug("Listening on port %s, starting reactor" % config.parameter("network", "port"))
reactor.run()
