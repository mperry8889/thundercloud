from twisted.internet import reactor
from thunderserver.restApi import createRestApi
from thundercloud import config
from thunderserver.orchestrator import Orchestrator
from thundercloud.spec.slave import SlaveSpec
from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue
import logging
import sys

from thundercloud.spec.user import UserSpec
from thunderserver.orchestrator.user import UserManager

from twisted.python import log as twistedLog

@inlineCallbacks
def startServer(port):
    logging.basicConfig(level=eval("logging.%s" % config.parameter("log", "level")))
    log = logging.getLogger("main")
    twistedLog.startLogging(sys.stderr)
    
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
    yield deferredList
    
    result = deferredList.result
    if result is not None:
        for (success, slaveId) in result:
            if success == False:
                log.error("Error adding slave")
            else:
                log.info("Slave %s connected" % slaveId)
    
    log.debug("Listening on port %s", port)
    reactor.listenTCP(port, createRestApi())
    
    
    # XXX
    userSpec = UserSpec()
    userSpec.username = "foo"
    userSpec.password = "foo"
    yield UserManager.create(userSpec)

    

if __name__ == "__main__":
    try:
        config.readConfig(sys.argv[1])
    except:
        print "No config file specified, exiting"
        sys.exit(1)
        
    reactor.callWhenRunning(startServer, config.parameter("network", "port", type=int))
    reactor.run()