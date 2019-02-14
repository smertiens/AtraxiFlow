#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.properties import PropertyObject
from atraxiflow.core.data import StringValueProcessor

class Node(PropertyObject):

    def get_name(self):
        return self.name

    def run(self, stream):
        raise Exception("Node class must implement run-method")

    def parse_string(self, stream, string):
        '''

        :return: StringValueProcessor
        '''
        return StringValueProcessor(stream).parse(string)


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
        return self.name;

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
