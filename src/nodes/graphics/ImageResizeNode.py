from nodes.foundation import ProcessorNode
from common import graphics

class ImageResizeNode(ProcessorNode):


    def __init__(self, name="", props=None):

        self.name = name
        self._known_properties = {
            'target_w' : {
                'label': "New width",
                'type': "text",
                'required': False,
                'hint': '',
                'default': 'auto'
            },
            'target_h': {
                'label': "New height",
                'type': "text",
                'required': False,
                'hint': '',
                'default': 'auto'
            },
            'source': {
                'label': "Resources to use",
                'type': "text",
                'required': False,
                'hint': '',
                'default': ''
            }
        }
        self.children = []
        self.listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}



    def run(self, stream):
        if not graphics.check_environment():
            return False

        if not self.check_properties():
            return False

        # Get resources for transform
        # Get file resources
        res = []

        if self.get_property('source') != '':
            res = stream.get_resources(self.get_property('source'))
        else:
            res += stream.get_resources('FS:*')
            res += stream.get_resources('Img:*')
