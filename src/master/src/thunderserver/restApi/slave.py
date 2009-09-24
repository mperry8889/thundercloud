from zope.interface import Interface, implements
from twisted.web.server import NOT_DONE_YET
import jsonpickle
import simplejson as json
import logging

from nodes import RootNode
from nodes import LeafNode
from nodes import Http400, Http404

from twisted.web import server, resource, guard
from twisted.web.resource import IResource
from twisted.cred.portal import IRealm, Portal

from ..orchestrator import Orchestrator
from thundercloud.spec.slave import SlaveSpec

log = logging.getLogger("restApi.slave")

class SlaveRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, Slave(), lambda: None
        raise NotImplementedError()

# Handle requests sent to /slave
class Slave(RootNode):

    def postCallback(self, slaveId, request):
        self.putChild("%d" % slaveId, SlaveNode())
        self.writeJson(request, slaveId)
    
    def postErrback(self, error, request):
        log.debug("Slave POST failed: %s" % error)
        self.writeJson(request, False)

    # create a new job based on the given JSON job spec
    def POST(self, request):
        request.content.seek(0, 0)
        slaveSpecObj = SlaveSpec(json.loads(request.content.read()))
        if not slaveSpecObj.validate():
            raise Http400, "Invalid request"
        
        deferred = Orchestrator.registerSlave(slaveSpecObj)
        deferred.addCallback(self.postCallback, request)
        deferred.addErrback(self.postErrback, request)
        return NOT_DONE_YET

class SlaveNode(LeafNode):
    pass

def RemoveStaleNode(slaveId):
    pass
