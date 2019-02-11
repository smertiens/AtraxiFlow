from nodes.foundation import ProcessorNode
import subprocess, os


class ShellExecNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'cmd' : {
                'type': "string",
                'required': True,
                'hint': 'Command to execute',
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
        os.system(self.get_property("cmd"))
