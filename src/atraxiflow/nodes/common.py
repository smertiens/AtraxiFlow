#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import time

from atraxiflow.core import *
from atraxiflow.properties import Property
from atraxiflow.resources import TextResource

__all__ = ['NullNode', 'EchoOutputNode', 'DelayNode', 'CLIInputNode']


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
