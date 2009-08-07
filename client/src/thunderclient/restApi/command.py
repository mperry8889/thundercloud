from nodes import RootNode
from nodes import LeafNode

from thunderclient.queue import ConnectionQueue

class Root(RootNode):
    pass

class Start(LeafNode):
    def render_GET(self, request):
        queue = ConnectionQueue(maxClients=2, requests=100, url="http://unshift.net")
        queue.start()
        return "ok"
        

CommandApiTree = Root()
CommandApiTree.putChild("", Root())
CommandApiTree.putChild("start", Start())
