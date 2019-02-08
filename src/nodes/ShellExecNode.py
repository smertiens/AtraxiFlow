from nodes.ProcessorNode import ProcessorNode
import subprocess, os

class ShellExecNode(ProcessorNode):

    _known_properties = {
        "cmd": {
            'type': "string",
            'required': True,
            'hint': 'Command to execute',
            'primary': True
        }
    }

    children = []

    def getNodeClass(self):
        return 'ShellExec'

    def run(self, stream):
        self.mergeProperties()
        os.system(self.getProperty("cmd"))
