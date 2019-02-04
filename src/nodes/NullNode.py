from nodes.ProcessorNode import *

class NullNode(ProcessorNode):

    _known_properties = {
        
    }

    def getNodeClass(self):
        return 'NullNode'

    def run(self, stream):
        pass