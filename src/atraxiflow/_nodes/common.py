#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import shlex
import subprocess
import os
import time
import platform

from atraxiflow.core import *
from atraxiflow.properties import *
from atraxiflow.base.resources import TextResource, FilesystemResource



class ExecNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'callable': {
                'label': 'Callable',
                'type': "string",
                'required': True,
                'hint': 'Callable to run'
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()

        obj = self.get_property('callable')
        stream.get_logger().debug('Executing {0}()'.format(obj))
        self._out = obj()


class EchoOutputNode(OutputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'msg': {
                'label': 'Message',
                'type': "string",
                'required': False,
                'hint': 'Text to output',
                "default": None
            }
        }

        self._known_inputs = {
            'resource': {
                'required': False,
                'hint': 'Resource to print',
                'accepts': [TextResource, FilesystemResource]
            }
        }

        self._listeners = {}
        self._inputs = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()
        self.check_inputs()

        if self.get_property('msg') is not None:
            print(self.parse_string(stream, self.get_property('msg')))

        if self.has_input('resource'):
            res = self.get_input('resource', True)[0]
            data = res.get_data()

            if type(data) in [dict, list, map, tuple]:
                for subdata in data:
                    print(subdata)
            else:
                print(data)

        return True


def echo(msg):
    """
    Convenience function to create an EchoOutputNode

    :param msg: The message to output
    :rtype: EchoOutputNode
    """

    return EchoOutputNode({'msg': msg})


class DelayNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'time': {
                'label': 'Time',
                'type': 'number',
                'required': False,
                'hint': 'Delay time in seconds',
                'default': 5
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_output(self):
        return None

    def run(self, stream):
        self.check_properties()

        time.sleep(int(self.get_property('time')))

        return True


class NullNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {}

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_output(self):
        return None

    def run(self, stream):
        return True


class CLIInputNode(InputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'save_to': {
                'label': 'Save to',
                'type': "string",
                'required': False,
                'hint': 'The name of the text resource to save the input to.',
                'default': 'last_cli_input'
            },
            'prompt': {
                'label': 'Prompt',
                'type': "string",
                'required': False,
                'hint': 'The text to display when prompting the user for input.',
                'default': 'Please enter: '
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()

        prompt = self.parse_string(stream, self.get_property('prompt'))
        user_input = input(prompt)

        if user_input == '':
            if self.get_property('on_empty') == 'fail':
                stream.get_logger().error('Input was empty. Stopping.')
                return False

        user_input_res = TextResource(self.get_property('save_to'), {"text": user_input})
        stream.add_resource(user_input_res)
        self._out = user_input_res
        return True
