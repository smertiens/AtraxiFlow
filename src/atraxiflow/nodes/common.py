#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import shlex
import subprocess
import sys
import time

from atraxiflow.nodes.foundation import *
from atraxiflow.nodes.text import TextResource


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

        stdout = ''
        stderr = ''
        if sys.version_info >= (3, 5):
            # using CompletedProcess
            result = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout = result.stdout.decode("utf-8")
            stderr = result.stderr.decode("utf-8")
        else:
            p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout_raw, stderr_raw = p.communicate()
            stdout = stdout_raw.decode("utf-8")
            stderr = stderr_raw.decode("utf-8")

        stream.add_resource(TextResource(self.get_property('output'), {'text': stdout}))
        stream.add_resource(TextResource(self.get_property('errors'), {'text': stderr}))


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


class NullNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {}

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        return True


class CLIInputNode(InputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'save_to': {
                'type': "string",
                'required': False,
                'hint': 'The name of the text resource to save the input to.',
                'default': 'last_cli_input'
            },
            'prompt': {
                'type': "string",
                'required': False,
                'hint': 'The text to display when prompting the user for input.',
                'default': 'Please enter: '
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        self.check_properties()

        prompt = self.parse_string(stream, self.get_property('prompt'))
        user_input = input(prompt)

        if user_input == '':
            if self.get_property('on_empty') == 'fail':
                logging.error('Input was empty. Stopping.')
                return False

        stream.add_resource(TextResource(self.get_property('save_to'), {"text": user_input}))
        return True
