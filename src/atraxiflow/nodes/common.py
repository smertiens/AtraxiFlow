#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import shlex
import subprocess
import time

from atraxiflow.core.data import StringValueProcessor
from atraxiflow.nodes.foundation import OutputNode
from atraxiflow.nodes.foundation import ProcessorNode
from atraxiflow.nodes.foundation import Resource


class ShellExecNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'cmd': {
                'type': "string",
                'required': True,
                'hint': 'Command to execute'
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
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        self.check_properties()
        args = shlex.split(self.get_property('cmd'))
        result = subprocess.run(args, capture_output=True)

        stream.add_resource(TextResource(self.get_property('output'), {'text': result.stdout.decode("utf-8")}))
        stream.add_resource(TextResource(self.get_property('errors'), {'text': result.stderr.decode("utf-8")}))


class EchoOutputNode(OutputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'msg': {
                'type': "string",
                'required': False,
                'hint': 'Text to output',
                'primary': True,
                "default": ''
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        self.check_properties()
        stp = StringValueProcessor(stream)
        print(stp.parse(self.get_property("msg")) + "\n")
        return True


class DelayNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'time': {
                'required': False,
                'hint': 'Delay time in seconds',
                'default': '5'
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        self.check_properties()

        time.sleep(int(self.get_property('time')))

        return True


class TextResource(Resource):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'text': {
                'label': "Text",
                'type': "string",
                'required': False,
                'hint': 'A simple text',
                'default': ''
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_prefix(self):
        return 'Text'

    def get_data(self):
        return self.get_property('text', '')

    def update_data(self, text):
        self.set_property('text', text)

    def __str__(self):
        return str(self.get_property('text', ''))


class NullNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {}

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        return True
