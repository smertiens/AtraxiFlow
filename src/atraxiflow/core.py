#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import importlib
import inspect
import logging
import pkgutil
from typing import List, Any, Dict

from PySide2 import QtWidgets
from atraxiflow.events import EventObject
from atraxiflow.exceptions import *
from atraxiflow.properties import Property, MissingRequiredValue
from atraxiflow.preferences import PreferencesProvider

__all__ = ['Node', 'Resource', 'Container', 'Workflow', 'WorkflowContext', 'get_node_info', 'run']


class Resource:
    """
    Resources need to create their own constructor. It should be possible to set the resources value
    via the constructor.
    A resources **id** is used to query resources of the given type inside a container. IDs must be **unique**
    to the specific resource, so they should use prefixing or the modules path.

    Assign a resources value to self._value or override :py:meth:`get_value` to use an other storage variable.

    .. code-block:: python

        def __init__(self, value=None):
            self._value = value
            self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
    """

    def get_value(self):
        """

        :return: The value of the resource
        """
        return self._value


class Container:
    """
    A container holds different resources and is used as the standard output of nodes.
    The content of a container can be queried using :py:meth:`find`.
    """

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
        """
        Returns the first item in the container or raise IndexError if Container is empty

        :return: The first item in the container
        """
        if len(self._items) == 0:
            raise IndexError()

        return self._items[0]

    def size(self) -> int:
        return len(self._items)

    def find(self, query: str) -> List[Resource]:
        """
        Finds resources in the current container.

        **Example queries**

        foo.bar: Find all resources with the id foo.bar
        *: Find all items
        *bar: Find resource id ending on "bar"
        foo*: Find resource id starting with "foo"

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
        lines = ['\t' + x.__class__.__name__ + ': ' + str(x) for x in self._items]
        lines.insert(0, 'Container:')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


class Node:
    """
    New nodes  should be initialized like this:

    .. code-block:: python

        def __init__(self, properties=None):
            user_properties = {
                # define your node's properties here
            }
            super().__init__(user_properties, properties)

    You can define additional properties of your node in the node classe's docstring using the following
    directives:

    @Name: Sets the node name as shown in Creator
    """

    def __init__(self, node_properties: Dict, user_properties: Dict, id: str = ''):
        self._input = None
        self.id = id if id != '' else '%s.%s' % (self.__module__, self.__class__.__name__)
        self.output = Container()
        self.properties = node_properties
        self.apply_properties(user_properties)

    def serialize(self) -> dict:
        """

        :return: Returns a dictionary with all property values
        """
        result = {}
        for name, prop in self.properties.items():
            result[name] = prop.value()

        return result

    def apply_ui_data(self):
        """
        This function is executed before the "run()" method in Creator. It should be used to write data from ui
        widgets to the properties of an underlying node object.
        """
        pass

    def load_ui_data(self):
        """
        This function is executed after the NodeWidget has been created from existing data (e.g. when loaded
        from a file). It can be used to fill custom widgets.
        """
        pass

    def get_ui(self, node_widget) -> QtWidgets.QWidget:
        """
        Override this function to create the user interface of your node in Creator completely by yourself.
        Remember to also override :py:meth:`apply_ui_data` and :py:meth:`load_ui_data` to keep node properties
        and user interface in sync.

        :param AxNodeWidget node_widget: The parent widget of the node's ui
        :return: The node's user interface
        """
        return None

    def get_field_ui(self, field_name: str, node_widget) -> QtWidgets.QWidget:
        """
        Overrides Creators default field for a property.

        :param str field_name: The name of the property whose ui is requested
        :param AxNodeWidget node_widget: The parent widget of the node's ui
        :return: Returns the ui for a single field
        """
        return None

    def get_properties(self) -> Dict[str, Property]:
        return self.properties

    def apply_properties(self, properties: dict):
        '''
        This function checks the given properties against the node's defined properties and will also set
        the default values. If a required value is not given, the value of the corresponding property is set to an
        instance of :py:class:`MissingRequiredValue`. The node should check for that class and raise an error if
        needed.

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

    def run(self, ctx) -> bool:
        """
        This is the main function of your node and must be overriden with the actual logic.

        :param WorkflowContext ctx: The current WorkflowContext
        :return: True if node execution was successful, False otherwise
        """
        return True

    def set_input(self, node):
        self._input = node

    def get_input(self) -> Container:
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
    """
    Holds information about the current workflow environment.
    It also takes care of extensions loading.
    """

    def __init__(self):
        self.preferences = PreferencesProvider()
        self._nodes = {}
        self._symbol_table = {}
        self.ui_env = False
        self.load_extensions()

    def autodiscover_nodes(self, root_package: str) -> list:
        """
        This function will return a list of node classes from a given python package/module.

        :param str root_package: The package/module path to look in
        :return: A list of node classes
        """

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

    def publish_nodes(self, group_name: str, nodes: list):
        """
        Publishes the given nodes to a group with the specified group_name in the current context.
        This way the nodes can be found by e.g. Creator

        :param str group_name: The name of the group
        :param list nodes: The nodes to publish - these can be loaded with :py:meth:`autodiscover_nodes`
        """
        self._nodes[group_name] = nodes

    def get_nodes(self) -> Dict[str, list]:
        return self._nodes

    def has_symbol(self, name: str) -> bool:
        return name in self._symbol_table

    def set_symbol(self, name: str, value: Any):
        if self.has_symbol(name):
            logging.getLogger('core').warning('Overriding existing symbol "{}"'.format(name))

        self._symbol_table[name] = value

    def get_symbol(self, name: str) -> Any:
        return self._symbol_table[name]

    def get_symbols(self) -> dict:
        return self._symbol_table

    def process_str(self, string: str) -> str:
        return string

    def get_registered_extensions(self):
        return self.preferences.get('extensions', ['atraxiflow.base'])

    def get_logger(self) -> logging.Logger:
        '''
        Returns the workflows logger for use by nodes
        :return: Logger
        '''
        return logging.getLogger('workflow_ctx')

    def load_extensions(self):
        """
        Loads all reqistered extensions.
        """
        self.get_logger().debug('Loading extensions...')

        for ext in self.get_registered_extensions():
            try:
                mod = importlib.import_module(ext + '.flow_extension')
            except ImportError:
                raise Exception('Error loading extension %s' % ext)

            if not hasattr(mod, 'boot'):
                raise Exception('Invalid extension: Missing boot method')

            logging.getLogger('core').debug('Booting "%s"...' % ext)
            mod.boot(self)


class Workflow(EventObject):
    EVENT_RUN_STARTED = "EVENT_RUN_STARTED"
    EVENT_RUN_FINISHED = "EVENT_RUN_FINISHED"
    EVENT_NODE_RUN_STARTED = "EVENT_NODE_RUN_STARTED"
    EVENT_NODE_RUN_FINISHED = "EVENT_NODE_RUN_FINISHED"

    def __init__(self, nodes: List[Node] = None):
        self._nodes = nodes if isinstance(nodes, list) else []
        self._ctx = WorkflowContext()
        self._listeners = {}

    def get_nodes(self):
        return self._nodes

    def get_context(self):
        return self._ctx

    def add_node(self, node: Node):
        self._nodes.append(node)

    @staticmethod
    def create(nodes: List[Node] = None):
        """ Convenience function to create a new stream """
        return Workflow(nodes)

    def __rshift__(self, node):
        """
        Add nodes via >> operator

        :param other: Node
        :return: Stream
        """
        if isinstance(node, Node):
            self.add_node(node)
        elif isinstance(node, str) and node == 'run':
            self.run()

        return self

    def run(self) -> bool:
        """
        Starts the workflow processing

        :return: bool - If false, errors have occured while processing the stream
        """
        self._ctx.get_logger().info("Starting processing")
        self.fire_event(self.EVENT_RUN_STARTED)
        self._pos = -1
        nodes_processed = 0
        prev_node = None

        for node in self._nodes:
            self._pos += 1

            if prev_node is not None:
                node.set_input(prev_node)

            self.fire_event(self.EVENT_NODE_RUN_STARTED, {'node': node})
            if self.get_context().ui_env:
                logging.getLogger('core').debug(
                    'Workflow started in UI environment, running apply_ui_data() on node...')
                node.apply_ui_data()

            logging.getLogger('core').debug("Running node {0}...".format(node.__class__.__name__))
            try:
                res = node.run(self._ctx)
            except Exception as e:
                logging.getLogger('core').error(e.__class__.__name__ + ': ' + str(e))
                self.fire_event(self.EVENT_RUN_FINISHED, {'errors': True, 'nodes_processed': nodes_processed})
                logging.getLogger('core').error('Stopping workflow execution due to an unexpected exception.')
                return False

            self.fire_event(self.EVENT_NODE_RUN_FINISHED, {'node': node})

            prev_node = node
            nodes_processed += 1

            if res is False:
                logging.getLogger('core').warning("Node failed.")
                logging.getLogger('core').info(
                    "Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
                self.fire_event(self.EVENT_RUN_FINISHED, {'errors': True, 'nodes_processed': nodes_processed})

                return False

        logging.getLogger('core').info("Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
        self.fire_event(self.EVENT_RUN_FINISHED, {'errors': False, 'nodes_processed': nodes_processed})
        return True


def run():
    """
    Is used with flow syntax to execute the current workflow
    """
    return 'run'


def get_node_info(node_object: object) -> dict:
    """
    Returns a dictionary with information on the given node extracted from the node's docstring.

    :param object node_object: Class or instance of node
    :return: Dict
    """
    docstr = inspect.getdoc(node_object)

    result = {
        'name': node_object.__name__ if hasattr(node_object, '__name__') else node_object.__class__.__name__,
        'accepts': [],
        'returns': [],
        'hide': False
    }

    if docstr is None:
        return result

    for line in docstr.split('\n'):
        line = line.lstrip()

        if not line.startswith('@'):
            continue

        k = line[1:line.find(':')].lower()
        val = line[line.find(':') + 1:].lstrip()

        if k == 'hide':
            val = True if val.lower() == 'true' else False

        if not k in result:
            raise KeyError('Unknown key: "%s"' % k)

        # TODO: reformat accepts/return
        result[k] = val

    return result
