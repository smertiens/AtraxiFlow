#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

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
                'label': 'Commmand',
                'type': "string",
                'required': True,
                'hint': 'Command to execute'
            },
            'output': {
                'label': 'Stdout',
                'type': "string",
                'required': False,
                'hint': 'Name of the TextResource to save output of the command to',
                'default': 'last_shellexec_out'
            },
            'errors': {
                'label': 'Stderr',
                'type': "string",
                'required': False,
                'hint': 'Name of the TextResource to save errors of the command to',
                'default': 'last_shellexec_errors'
            },
            'echo_command': {
                'label': 'Echo command',
                'type': "boolean",
                'required': False,
                'default': False
            },
            'echo_output': {
                'label': 'Echo output',
                'type': "boolean",
                'required': False,
                'default': False
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()
        cmd = self.parse_string(stream, self.get_property('cmd'))
        args = shlex.split(cmd)

        stdout = ''
        stderr = ''

        if self.get_property('echo_command') is True:
            print(cmd)

        result = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if self.get_property('echo_output') is True:
            while result.poll() is None:
                line = result.stdout.readline().decode('utf-8')
                print(line.replace('\n', ''))
                stdout += line
                line = result.stderr.readline().decode('utf-8')
                print(line.replace('\n', ''))
                stderr += line
        else:
            stdout_raw, stderr_raw = result.communicate()
            stdout = stdout_raw.decode("utf-8")
            stderr = stderr_raw.decode("utf-8")

        if stream.get_resource_by_name(self.get_property('output')) is not None:
            stream.remove_resource('Text:{0}'.format(self.get_property('output')))

        if stream.get_resource_by_name(self.get_property('errors')) is not None:
            stream.remove_resource('Text:{0}'.format(self.get_property('errors')))

        res_out = TextResource(self.get_property('output'), {'text': stdout})
        res_err = TextResource(self.get_property('errors'), {'text': stderr})
        stream.add_resource(res_err)
        stream.add_resource(res_out)
        self._out = [res_out, res_err]


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
            },
            'res': {
                'label': 'Resource',
                'type': "resource_query",
                'required': False,
                'hint': 'Resource query to be output',
                "default": None
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()

        if self.get_property('msg') is not None:
            print(self.parse_string(stream, self.get_property('msg')))

        if self.get_property('res') is not None:

            resources = stream.get_resources(self.get_property('res'))

            for res in resources:
                data = res.get_data()

                if type(data) in [dict, list, map, tuple]:
                    for subdata in data:
                        print(subdata)
                else:
                    print(data)

        return True


class DelayNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'time': {
                'label': 'Time',
                'type': 'number',
                'required': False,
                'hint': 'Delay time in seconds',
                'default': '5'
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
