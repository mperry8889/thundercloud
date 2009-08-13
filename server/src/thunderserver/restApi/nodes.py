from twisted.web.resource import Resource
from zope.interface import Interface, implements

class Node(Resource):
    pass
    
class RootNode(Node):
    isLeaf = False
   
class LeafNode(Node):
    isLeaf = True