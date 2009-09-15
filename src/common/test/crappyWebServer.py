# this is a crappy webserver, which returns a variety of error codes at random

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet.defer import inlineCallbacks

from thundercloud.spec.job import JobSpec
from thundercloud.util.restApiClient import RestApiClient

class CrappyResource(Resource):
    pass