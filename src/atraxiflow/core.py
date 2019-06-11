#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.exceptions import *
from atraxiflow.properties import Property
import logging

__all__ = ['Node', 'Resource', 'Container', 'Workflow']


class Container:

    def __init__(self, *kwargs):
        self._items = []

        for item in kwargs:
            self._items.append(item)

    def add(self, item):
        self._items.append(item)

    def items(self):
        return self._items

    def find(self, query):
        return []

    def __str__(self):
        lines = ['\t' + str(x) for x in self._items]
        lines.insert(0, 'Container:')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


class Node:
    """
    New nodes  should be initialized like this:

    def __init__(self, properties):
        self.output = Container()
        self.properties = {}
        self.id = '%s.%s' % (self.__module__, self.__name__)
        self._input = None

        self.apply_properties(properties)

    """

    def apply_properties(self, properties):
        '''
        Check and merge properties

        :return: boolean
        '''

        for name, property in self.properties.items():
            if not isinstance(property, Property):
                raise ValueError()

            if name not in properties and property.is_required():
                raise PropertyException('Property %s is required' % name)
            elif name not in properties:
                self.property(name).set(property.get_default())

            if name in properties:
                if not property.validate(properties[name]):
                    raise PropertyException('Invalid value for %s' % name)

                self.property(name).set(properties[name])

    def property(self, name):
        if not name in self.properties:
            raise PropertyNotFoundException('Property %s not found' % name)

        return self.properties[name]

    def run(self):
        raise Exception("Node class must implement run-method")

    def set_input(self, node):
        self._input = node

    def get_input(self):
        return self._input

    def get_output(self):
        return self.output


class Resource:
    """
    def __init__(self):
        self._value = None
        self.id = '%s.%s' % (self.__module__, self.__name__)
    """
    pass


class Workflow:

    def __init__(self, nodes=None):
        self._nodes = nodes if isinstance(nodes, list) else []

    def add_node(self, node):
        self._nodes.append(node)

    def get_logger(self):
        '''
        Returns the streams logger
        :return: Logger
        '''
        return logging.getLogger('stream')

    @staticmethod
    def create(nodes = None):
        ''' Convenience function to create a new stream '''
        return Workflow(nodes)

    def __rshift__(self, node):
        '''
        Add nodes via >> operator

        :param other: Node
        :return: Stream
        '''
        if isinstance(node, Node):
            self.add_node(node)
        elif isinstance(node, str) and node == 'run':
            self.run()

        return self

    def run(self):
        '''
        Starts the workflow processing

        :return: bool - If false, errors have occured while processing the stream
        '''
        self.get_logger().info("Starting processing")
        # self.fire_event(self.EVENT_STREAM_STARTED)
        self._pos = -1
        nodes_processed = 0

        for node in self._nodes:
            self._pos += 1

            self.get_logger().debug("Running node {0}".format(node.__class__.__name__))
            # self.fire_event(self.EVENT_NODE_STARTED)
            res = node.run()
            nodes_processed += 1
            # self.fire_event(self.EVENT_NODE_FINISHED)

            if res is False:
                self.get_logger().warning("Node failed.")
                self.get_logger().info(
                    "Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
                # self.fire_event(self.EVENT_STREAM_FINISHED)

                return False

        self.get_logger().info("Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
        # self.fire_event(self.EVENT_STREAM_FINISHED)
        return True

def run():
    return 'run'