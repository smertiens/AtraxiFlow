from nodes.OutputNode import *
from common.StringProcessor import StringProcessor

class EchoOutputNode(OutputNode):
    _known_properties = {
        'text': {
            'type': "string",
            'required': True,
            'hint': 'Text to output',
            'primary': True
        }
    }

    children = []

    def getNodeClass(self):
        return 'EchoOutput'

    def run(self, stream):
        self.mergeProperties()
        stp = StringProcessor(stream)
        print(stp.parse(self.getProperty("text")) + "\n")