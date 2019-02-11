from nodes.foundation import OutputNode
from common.data import StringValueProcessor


class EchoOutputNode(OutputNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'text': {
                'type': "string",
                'required': True,
                'hint': 'Text to output',
                'primary': True
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def run(self, stream):
        self.check_properties()
        stp = StringValueProcessor(stream)
        print(stp.parse(self.get_property("text")) + "\n")
