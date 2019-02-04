from nodes.OutputNode import *
from StringProcessor import StringProcessor

class EchoOutputNode(OutputNode):
    _known_properties = {
        'text': {
            'type': str,
            'required': True,
            'hint': 'Text to output'
        }
    }

    children = []

    def getNodeClass(self):
        return 'EchoOutput'

    def run(self, stream):
        self.checkProperties()
        stp = StringProcessor(stream)
        print(stp.parse(self.getProperty("text")) + "\n")