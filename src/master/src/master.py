from twisted.internet import reactor
from thunderserver.restApi import createRestApi
from thundercloud import config
from thunderserver.orchestrator import Orchestrator
from thundercloud.spec.slave import SlaveSpec
from twisted.internet.defer import DeferredList
import logging
import sys

from twisted.python import log as twistedLog

try:
    config.readConfig(sys.argv[1])
except:
    print "No config file specified, exiting"
    sys.exit(1)


def registerSlaveCallback(value):
    for (success, slaveId) in value:
        if success == False:
            log.error("Error adding slave")
        else:
            log.info("Slave %s connected" % slaveId)

def registerSlaveErrback():
    pass

logging.basicConfig(level=eval("logging.%s" % config.parameter("log", "level")))
log = logging.getLogger("main")

# try the epoll reactor if it's available
try:
    from twisted.internet import epollreactor
    epollreactor.install()
    log.debug("Using epoll reactor")
except:
    log.debug("Using default select reactor")



# add slaves in the INI file if they're around and add-able
slaves = {}
for (key, val) in config.section("slave"):
    slaveNo = key[:key.find(".")]
    attr = key[key.find(".")+1:]
    
    try:
        setattr(slaves[slaveNo], attr, val)
    except KeyError:
        slaves[slaveNo] = SlaveSpec()
        setattr(slaves[slaveNo], attr, val)
    
    
deferreds = []
for slaveSpec in slaves.itervalues():
    log.info("Connecting slave: %s" % slaveSpec)
    deferreds.append(Orchestrator.registerSlave(slaveSpec))

deferredList = DeferredList(deferreds)
deferredList.addCallback(registerSlaveCallback)

log.debug("Listening on port %s, starting reactor" % config.parameter("network", "port"))
reactor.listenTCP(config.parameter("network", "port", type=int), createRestApi())
twistedLog.startLogging(sys.stderr)

reactor.run()
