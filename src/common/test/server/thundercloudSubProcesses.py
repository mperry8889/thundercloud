from twisted.internet import reactor

import signal
import os
import sys
import time

from thundercloud import config
from multiprocessing import Process

def createMasterSubProcess(port):
    def runMaster(port):
        from thundercloud import config
        import thunderserver
        config._config.add_section("network")
        config._config.set("network", "port", "%s" % port)
        config._config.set("network", "authentication", "false")
        config._config.add_section("log")
        config._config.set("log", "level", "debug")
        config._config.add_section("slave")
        reactor.callWhenRunning(thunderserver.startServer, port)
        reactor.run()
    process = Process(target=runMaster, args=(port,))
    process.start()
    return process

def createSlaveSubProcess(port, masterPort):
    def runSlave(port, masterPort):
        from thundercloud import config
        import thunderslave
        config._config.add_section("network")
        config._config.set("network", "port", "%s" % port)
        config._config.set("network", "authentication", "false")
        config._config.set("network", "clients.max", "1000")
        config._config.add_section("log")
        config._config.set("log", "level", "debug")
        config._config.add_section("master")
        config._config.set("master", "scheme", "http")
        config._config.set("master", "host", "127.0.0.1")
        config._config.set("master", "port", "%s" % masterPort)
        config._config.set("master", "path", "/")
        config._config.add_section("misc")
        config._config.set("misc", "standalone", "false")
        reactor.callWhenRunning(thunderslave.startServer, port)
        reactor.run()
    process = Process(target=runSlave, args=(port, masterPort))
    process.start()
    return process