from nodes.ProcessorNode import *

class NullNode(ProcessorNode):

    _known_properties = {
        
    }

    def getNodeType(self):
        return 'NullNode'

    def run(self, stream):
        pass