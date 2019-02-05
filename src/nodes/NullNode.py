from nodes.ProcessorNode import *

class NullNode(ProcessorNode):

    _known_properties = {
        
    }

    children = []

    def getNodeClass(self):
        return 'NullNode'

    def run(self, stream):
        pass