from twisted.internet import reactor
from thunderslave.restApi import createRestApi
from thundercloud import config
import logging
import sys

try:
    config.readConfig(sys.argv[1])
except:
    print "No config file specified, exiting"
    sys.exit(1)

logging.basicConfig(level=eval("logging.%s" % config.parameter("log", "level")))
log = logging.getLogger("main")

log.debug("Listening on port %s, starting reactor" % config.parameter("network", "port"))
reactor.listenTCP(int(config.parameter("network", "port")), createRestApi())

reactor.run()
