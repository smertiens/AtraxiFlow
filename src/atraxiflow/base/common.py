#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
import platform
import shlex
import subprocess
import time

from atraxiflow.base.resources import TextResource
from atraxiflow.core import *
from atraxiflow.properties import Property

__all__ = ['NullNode', 'EchoOutputNode', 'DelayNode', 'CLIInputNode', 'ShellExecNode']


class ShellExecNode(Node):
    """
    @Name: Execute console command
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'cmd': Property(expected_type=str, required=True, label='Command',
                            hint='Command to execute', default=''),
            'echo_cmd': Property(expected_type=bool, required=False, default=False, label='Echo command'),
            'echo_output': Property(expected_type=bool, required=False, default=False, label='Echo output')
        }

        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

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
    """
    @Name: Write to console
    """

    def __init__(self, properties=None):
        node_properties = {
            'msg': Property(expected_type=str, required=False, hint='Text to output', label='Message')
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        if self.property('msg').value() is not None:
            print(ctx.process_str(self.property('msg').value()))

        if self.has_input():
            for res in self.get_input().find('*'):
                print(res)

        return True


class DelayNode(Node):
    """
    @Name: Add delay
    """

    def __init__(self, properties=None):
        node_properties = {
            'time': Property(expected_type=(float, int), required=False, hint='Time to sleep (in seconds)',
                             label='Time')
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        time.sleep(int(self.property('time').value()))

        return True


class NullNode(Node):
    """
    @Hide: True
    """

    def __init__(self, properties=None):
        super().__init__({}, properties)

    def run(self, ctx: WorkflowContext):
        return True


class CLIInputNode(Node):
    """
    @Name: Get user input from console
    """

    def __init__(self, properties=None):
        user_properties = {
            'prompt': Property(expected_type=str, required=False, label='Prompt',
                               hint='The text to display when prompting the user for input.', default='')
        }
        super().__init__(user_properties, properties)

    def run(self, ctx: WorkflowContext) -> bool:
        super().run(ctx)
        prompt = ctx.process_str(self.property('prompt').value())
        user_input = input(prompt)

        # if user_input == '':
        #     if self.get_property('on_empty') == 'fail':
        #         stream.get_logger().error('Input was empty. Stopping.')
        #         return False

        self.output.add(TextResource(user_input))
        return True
