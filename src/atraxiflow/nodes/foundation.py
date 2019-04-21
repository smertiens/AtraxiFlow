#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

__all__ = ['Node', 'ProcessorNode', 'OutputNode', 'InputNode', 'Resource']

from atraxiflow.core.data import StringValueProcessor
from atraxiflow.core.properties import PropertyObject
from atraxiflow.core.exceptions import *


class Node(PropertyObject):
    EVENT_INPUTS_CHANGED = 'inputs_changed'
    EVENT_INPUTS_CHECKED = 'inputs_checked'

    def get_name(self):
        return self.name

    def set_stream(self, stream):
        self._stream = stream

    def run(self, stream):
        raise Exception("Node class must implement run-method")

    def parse_string(self, stream, string):
        '''

        :return: StringValueProcessor
        '''
        return StringValueProcessor(stream).parse(string)

    def get_output(self):
        raise Exception("Node class must implement get_output-method")

    def connect(self, entity, input_name=None):
        if not hasattr(self, '_inputs'):
            # Node has no inputs
            raise InputException('Node does not support inputs')

        if input_name not in self._known_inputs:
            raise InputException('Node does not have input "{0}"'.format(input_name))

        if input_name in self._inputs:
            limit = self._known_inputs[input_name]['limit'] if 'limit' in self._known_inputs[input_name] else 1

            # if limit is reached, remove item
            if len(self._inputs[input_name]) == limit and limit > 0:
                self._inputs[input_name].pop()

            self._inputs[input_name].append(entity)
        else:
            self._inputs[input_name] = [entity]

    def disconnect(self, input_name, entity=None):

        if not hasattr(self, '_inputs'):
            # Node has no inputs
            raise InputException('Node does not support inputs')

        if input_name not in self._inputs:
            raise InputException('Node does not have input "{0}"'.format(input_name))

        if entity is None:
            self._inputs[input_name] = []
        else:
            if entity not in self._inputs[input_name]:
                raise InputException('Disconnect failed: No connection found.')
            else:
                self._inputs[input_name].remove(entity)

    def get_input(self, input_name, resolve=True):
        if resolve is True:
            resources = self._inputs[input_name]
            new_list = []

            for res in resources:
                if isinstance(res, Node):
                    new_list.append(res.get_output())
                else:
                    new_list.append(res)

            return new_list
        else:
            return self._inputs[input_name]

    def has_input(self, input_name):
        return input_name in self._inputs and len(self._inputs[input_name]) > 0

    def check_inputs(self):
        '''
        Validate all inputs

        :return: boolean
        '''

        for name, opts in self._known_inputs.items():

            if 'required' in opts and opts['required'] is True and name not in self._inputs:
                self.fire_event(self.EVENT_INPUTS_CHECKED, False)
                raise InputException('Required input "{0}" not set.'.format(name))

            elif name in self._inputs:
                if 'accepts' not in opts:
                    self.fire_event(self.EVENT_INPUTS_CHECKED, False)
                    raise InputException('Nodes must define the "accepts" property for every input.')

                for item in self._inputs[name]:
                    if isinstance(item, Node):
                        item = item.get_output()

                    if type(item) not in opts['accepts']:
                        raise InputException('Object "{0}" not accepted by this input.'.format(item))


class ProcessorNode(Node):
    pass


class OutputNode(Node):
    pass


class InputNode(Node):
    pass


class Resource(PropertyObject):

    def parse_string(self, stream, string):
        '''

        :return: StringValueProcessor
        '''
        return StringValueProcessor(stream).parse(string)

    def get_name(self):
        '''
        Returns the name of the resource
        :return: str
        '''
        return self.name

    def get_prefix(self):
        '''
        Returns the resource prefix
        :return: str
        '''
        raise Exception("Resources must overwrite getPrefix()")

    def get_data(self):
        pass

    def update_data(self, data):
        pass

    def resolve_variable(self, varname):
        return self.get_data()

    def set_stream(self, stream):
        self._stream = stream
