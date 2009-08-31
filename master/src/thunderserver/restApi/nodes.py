from twisted.web.resource import Resource
from zope.interface import Interface, implements

class Http400(Exception):
    pass

class Http404(Exception):
    pass

class Node(Resource):
    pass
    
class RootNode(Node):
    isLeaf = False
   
class LeafNode(Node):
    isLeaf = True