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
from atraxiflow.properties import Property
from atraxiflow.base.resources import TextResource

__all__ = ['NullNode', 'EchoOutputNode', 'DelayNode', 'CLIInputNode', 'ShellExecNode']

class ShellExecNode(Node):

    def __init__(self, properties: dict = None):
        self.output = Container()
        self.properties = {
            'cmd': Property(expected_type=str, required=True, label='Command',
                                          hint='Command to execute', default=''),
            'echo_cmd': Property(expected_type=bool, required=False, default=False, label='Echo command'),
            'echo_output': Property(expected_type=bool, required=False, default=False, label='Echo output')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None
        self.apply_properties(properties)


    def run(self, ctx: WorkflowContext):
        cmd = ctx.process_str(self.property('cmd').value())
        args = shlex.split(cmd)

        stdout = ''
        stderr = ''

        if self.property('echo_cmd').value() is True:
            print(cmd)

        if platform.system() == 'Windows':
            # this will invoke a system shell on windows and should not interfere with executing
            # other binaries.
            result = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        else:
            result = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if self.property('echo_output').value() is True:
            while result.poll() is None:
                line = result.stdout.readline().decode('utf-8').replace(os.linesep, '')
                if line != '':
                    print(line)
                    stdout += line

                line = result.stderr.readline().decode('utf-8').replace(os.linesep, '')
                if line != '':
                    print(line)
                    stderr += line
        else:
            stdout_raw, stderr_raw = result.communicate()
            stdout = stdout_raw.decode("utf-8")
            stderr = stderr_raw.decode("utf-8")

        res_out = TextResource(stdout)
        res_err = TextResource(stderr)
        self.output = Container(res_out, res_err)


class EchoOutputNode(Node):

    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {
            'msg': Property(expected_type=str, required=False, hint='Text to output', label='Message')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext):
        if self.property('msg') is not None:
            print(self.property('msg').value())

        if self.has_input():
            for res in self.get_input().find('*'):
                print(res)

        return True


class DelayNode(Node):

    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {
            'time': Property(expected_type=(int, float), required=False, hint='Time to sleep', label='Time')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext):
        time.sleep(int(self.property('time').value()))

        return True


class NullNode(Node):

    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {}
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext):
        return True


class CLIInputNode(Node):

    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {
            'prompt': Property(expected_type=str, required=False,
                               hint='The text to display when prompting the user for input.', default='')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None
        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext) -> bool:
        prompt = ctx.process_str(self.property('prompt').value())
        user_input = input(prompt)

        # if user_input == '':
        #     if self.get_property('on_empty') == 'fail':
        #         stream.get_logger().error('Input was empty. Stopping.')
        #         return False

        self.output.add(TextResource(user_input))
        return True

"""
class ExecNode(Node):
    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {
            'callable': Property(expected_type=str, required=True,hint='Callable to run', label='Callable')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None
        self.apply_properties(properties)


    def run(self, ctx: WorkflowContext):
        obj = self.property('callable').value()
        ctx.get_logger().debug('Executing {0}()'.format(obj))
        self.output = Container(obj())
"""