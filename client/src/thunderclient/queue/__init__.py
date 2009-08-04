from Queue import Queue
from twisted.internet import reactor
from time import sleep
import logging as log

from twisted.web.client import HTTPClientFactory
from twisted.web.client import getPage

class ConnectionQueue():
    """State machine to manage a connection queue"""
    
    __queue = Queue()
    
    __active = 0
    __completed = 0
    __maxClients = 0
    __sleepDelay = 0.0
    __httpClientFactory = None
    
    
    def __init__(self, maxClients=2, requests=10, url="http://unshift.net"):
        if maxClients < 0:
            raise ValueError("maxClients must be > 0")
        if requests < 0:
            raise ValueError("requests must be > 0")
#        if type(httpClientFactory) != HTTPClientFactory:
#            raise ValueError("http request must be of type twisted.web.client.HTTPClientFactory")

        self.__maxClients = maxClients
        self.__requests = requests
        self.__sleepDelay = 1000
#        self.__httpClientFactory = httpClientFactory
        
        for i in range(1, self.__requests+1):
            self.__queue.put(i)
    
    
    def start(self):
        while self.__active < self.__maxClients:
            self.__pop()
    
    def pause(self):
        self.__maxClients = 0
    
    
    def __callback(self, value, request):
        # mark request as inactive and complete
        self.__active = self.__active - 1        
        self.__completed = self.__completed + 1

        if self.__completed >= self.__requests-1:
            return
        
        # restart loop
        self.start()

    
    def __errback(self, value, request):
        self.__active = self.__active - 1
        self.__completed = self.__completed + 1

    
    def __pop(self):       
        # queue is empty - abort
        if self.__queue.empty():
            return
        
        # mark a client as active, and pop the queue
        self.__active = self.__active + 1
        request = self.__queue.get()
        
        sleep(self.__sleepDelay/1000)
        deferred = getPage("http://unshift.net")
        deferred.addCallback(self.__callback, request) 
        deferred.addErrback(self.__errback, request)
        
#        d = self.__httpClientFactory()
        