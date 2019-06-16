#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging

from PySide2 import QtWidgets
from atraxiflow.exceptions import *
from atraxiflow.properties import Property, MissingRequiredValue
import importlib, pkgutil, inspect
from typing import List, Any, Dict

__all__ = ['Node', 'Resource', 'Container', 'Workflow', 'WorkflowContext']

class Resource:
    """
    def __init__(self, value=None):
        self._value = value
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
    """

    def get_value(self):
        return self._value


class Container:

    def __init__(self, *kwargs):
        self._items = []

        for item in kwargs:
            self._items.append(item)

    def clear(self):
        self._items.clear()

    def add(self, item: Resource):
        self._items.append(item)

    def items(self) -> List[Resource]:
        return self._items

    def first(self) -> Resource:
        if len(self._items) == 0:
            raise IndexError()

        return self._items[0]

    def find(self, query: str) -> List[Resource]:
        """

        foo.bar: Return item with the id foo.bar
        *: Return all items
        *bar: Item id ending on "bar"
        foo*: Item id starting with "foo"

        :param str query: Query string
        :return: Resources
        :rtype: list
        """

        result = []
        if not '*' in query:
            result = [item for item in self._items if item.id == query]
        else:
            if query == '*':
                result = self._items
            elif query.startswith('*'):
                result = [item for item in self._items if item.id.endswith(query[1:])]
            elif query.endswith('*'):
                result = [item for item in self._items if item.id.startswith(query[:-1])]

        return result

    def __str__(self):
        lines = ['\t' + str(x) for x in self._items]
        lines.insert(0, 'Container:')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


class Node:
    """
    New nodes  should be initialized like this:

    def __init__(self, properties = None):
        self.output = Container()
        self.user_properties = properties
        self.properties = {}
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        # Optional:
        self.node_name = '' | Classname

        # in run()
        self.apply_properties(self.user_properties)

    """

    def __init__(self, node_properties: Dict, user_properties: Dict, id:str = ''):
        self._input = None
        self.id = id if id != '' else '%s.%s' % (self.__module__, self.__class__.__name__)
        self.output = Container()
        self.properties = node_properties
        self.apply_properties(user_properties)

    @staticmethod
    def get_name() -> str:
        return ''

    def get_ui(self)->QtWidgets.QWidget:
        return None

    def get_field_ui(self, field_name:str) -> QtWidgets.QWidget:
        return None

    def get_properties(self) -> Dict[str, Property]:
        return self.properties

    def apply_properties(self, properties: dict):
        '''
        Check and merge properties

        :return: boolean
        '''

        if properties is None:
            properties = {}

        for name, property in self.properties.items():
            if not isinstance(property, Property):
                raise ValueError()

            if name not in properties and property.is_required():
                self.property(name).set_value(MissingRequiredValue())
            elif name not in properties:
                self.property(name).set_value(property.get_default())

            if name in properties:
                if not property.validate(properties[name]):
                    raise PropertyException('Invalid value for %s' % name)

                self.property(name).set_value(properties[name])


    def property(self, name) -> Property:
        if not name in self.properties:
            raise PropertyNotFoundException('Property %s not found' % name)

        return self.properties[name]

    def run(self, ctx):
        for name, property in self.properties.items():
            if isinstance(property.value(), MissingRequiredValue):
                raise Exception('Property "{}" is required'.format(name))

    def set_input(self, node):
        self._input = node

    def get_input(self):
        """

        :return: The output of the connected input node
        :rtype: Container
        """
        if isinstance(self._input, Node):
            return self._input.get_output()
        else:
            raise ValueError('Input has to be a node')

    def has_input(self) -> bool:
        return self._input is not None

    def get_output(self) -> Container:
        return self.output


class WorkflowContext:

    def __init__(self):
        self._nodes = {}
        self._symbol_table = {}
        self.load_extensions()

    def autodiscover_nodes(self, root_package: str)-> list:

        def collect_module_data(mod):
            result = []

            for attr in dir(mod):
                o = getattr(mod, attr)
                if not hasattr(o, '__bases__'):
                    continue

                if Node in o.__bases__:
                    result.append(o)

            return result

        result = []
        pkg = importlib.import_module(root_package)

        if inspect.ismodule(pkg):
            result += collect_module_data(pkg)
        else:
            for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                if not ispkg:
                    mod = importlib.import_module(root_package + '.' + modname)
                    result += collect_module_data(mod)

        return result

    def publish_nodes(self, group_name: str, nodes: dict):
        self._nodes[group_name] = nodes

    def get_nodes(self)->Dict[str, list]:
        return self._nodes

    def has_symbol(self, name: str)->bool:
        return name in self._symbol_table

    def set_symbol(self, name:str, value: Any):
        if self.has_symbol(name):
            self.get_logger().warning('Overriding existing symbol "{}"'.format(name))

        self._symbol_table[name] = value

    def get_symbol(self, name: str)->Any:
        return self._symbol_table[name]

    def get_symbols(self) -> dict:
        return self._symbol_table

    def process_str(self, string: str) -> str:
        return string

    def get_registered_extensions(self):
        return ['atraxiflow.base']

    def get_logger(self) -> logging.Logger:
        '''
        Returns the streams logger
        :return: Logger
        '''
        return logging.getLogger('workflow')

    def load_extensions(self):
        for ext in self.get_registered_extensions():
            try:
                mod = importlib.import_module(ext + '.flow_extension')
            except ImportError:
                raise Exception('Error loading extension %s' % ext)

            if not hasattr(mod, 'boot'):
                raise Exception('Invalid extension: Missing boot method')

            mod.boot(self)

class Workflow:

    def __init__(self, nodes: List[Node]=None):
        self._nodes = nodes if isinstance(nodes, list) else []
        self._ctx = WorkflowContext()

    def add_node(self, node: Node):
        self._nodes.append(node)

    @staticmethod
    def create(nodes: List[Node]=None):
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

    def run(self) -> bool:
        '''
        Starts the workflow processing

        :return: bool - If false, errors have occured while processing the stream
        '''
        self._ctx.get_logger().info("Starting processing")
        # self.fire_event(self.EVENT_STREAM_STARTED)
        self._pos = -1
        nodes_processed = 0
        prev_node = None

        for node in self._nodes:
            self._pos += 1

            self._ctx.get_logger().debug("Running node {0}".format(node.__class__.__name__))
            # self.fire_event(self.EVENT_NODE_STARTED)
            if prev_node is not None:
                node.set_input(prev_node)

            res = node.run(self._ctx)
            prev_node = node
            nodes_processed += 1
            # self.fire_event(self.EVENT_NODE_FINISHED)

            if res is False:
                self._ctx.get_logger().warning("Node failed.")
                self._ctx.get_logger().info(
                    "Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
                # self.fire_event(self.EVENT_STREAM_FINISHED)

                return False

        self._ctx.get_logger().info("Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
        # self.fire_event(self.EVENT_STREAM_FINISHED)
        return True


def run():
    return 'run'
