from twisted.internet import reactor
from thundercloud import config
import thunderserver
import sys

if __name__ == "__main__":
    try:
        config.readConfig(sys.argv[1])
    except:
        print "No config file specified, exiting"
        sys.exit(1)
        
    reactor.callWhenRunning(thunderserver.startServer, config.parameter("network", "port", type=int))
    reactor.run()