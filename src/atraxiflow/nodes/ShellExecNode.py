#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.nodes.foundation import ProcessorNode
import subprocess, os, shlex
from atraxiflow.nodes.TextResource import  TextResource


class ShellExecNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'cmd' : {
                'type': "string",
                'required': True,
                'hint': 'Command to execute',
                'primary': True
            },
            'output': {
                'type': "string",
                'required': False,
                'hint': 'Name of the TextResource to save output of the command to',
                'default': 'last_shellexec_out'
            },
            'errors': {
                'type': "string",
                'required': False,
                'hint': 'Name of the TextResource to save errors of the command to',
                'default': 'last_shellexec_errors'
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
        args = shlex.split(self.get_property('cmd'))
        result = subprocess.run(args, capture_output=True)

        stream.add_resource(TextResource(self.get_property('output'), {'text': result.stdout.decode("utf-8")}))
        stream.add_resource(TextResource(self.get_property('errors'), {'text': result.stderr.decode("utf-8")}))
