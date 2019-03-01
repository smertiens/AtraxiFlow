#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
from threading import Thread

from atraxiflow.core.events import EventObject
from atraxiflow.core.gui import *
from atraxiflow.gui import GUI
from atraxiflow.nodes.foundation import Node, Resource


def flow():
    return 'flow'


def flow_ui():
    return 'flow_ui'


class AsyncBranch(Thread):
    '''
    This class represents a branch of an existing stream that is executed in a separate thread
    '''

    def __init__(self, name, stream):
        '''

        :param name: The branch name
        :param stream: The stream that should run in the branch
        '''
        super().__init__()

        self._nodes = []
        self.name = name
        self.stream = stream

    def set_stream(self, stream):
        ''' Set stream '''
        self.stream = stream

    def get_stream(self):
        '''
        Get the stream
        :return: Stream
        '''
        return self.stream

    def get_name(self):
        '''
        Returns the branch name
        :return: str
        '''
        return self.name

    def run(self):
        '''
        Starts the stream of this branch
        :return: bool
        '''
        self.stream.get_logger().info("Starting new thread on branch {0}".format(self.get_name()))
        return self.stream.flow()


class Stream(EventObject):
    '''
    The main building block of a workflow. Streams hold all nodes and resources
    '''

    EVENT_STREAM_STARTED = 0
    EVENT_STREAM_FINISHED = 1
    EVENT_NODE_STARTED = 0
    EVENT_NODE_FINISHED = 1

    def __init__(self):
        self._resource_map = {}
        self._branch_map = {}
        self._nodes = []
        self._listeners = {}

        self._gui_ctx = None

    def set_gui_context(self, ctx):
        '''
        Holds a reference to a gui singleton (like QApplication)
        :param ctx: The context instance
        :return:
        '''
        self._gui_ctx = ctx

    def get_gui_context(self):
        '''
        Returns current gui context
        :return: object
        '''
        return self._gui_ctx

    def __rshift__(self, other):
        '''
        Add nodes via >> operator

        :param other: Node or Resource
        :return: Stream
        '''
        if isinstance(other, Node):
            self.append_node(other)
        elif isinstance(other, Resource):
            self.add_resource(other)
        elif isinstance(other, str) and other == 'flow':
            self.flow()
        elif isinstance(other, str) and other == 'flow_ui':
            gui = GUI(self)
            gui.flow()

        return self

    def get_node_count(self):
        return len(self._nodes)

    def get_logger(self):
        '''
        Returns the streams logger
        :return: Logger
        '''
        return logging.getLogger('stream')

    def set_log_level(self, level):
        '''
        Sets the global log level. Use levels from pythons logging module.

        :param level: logging Log level
        :return: Stream
        '''

        self.get_logger().setLevel(level)
        return self

    def create():
        ''' Convenience function to create a new stream '''
        return Stream()

    def branch(self, name):
        '''
        Create a new branch

        :param name: The name of the new branch
        :return: bool
        '''
        branch = AsyncBranch(name, Stream())
        self.append_node(branch)
        self._branch_map[branch.get_name()] = branch
        return branch.get_stream()

    def get_branch(self, name):
        '''
        Returns a branch

        :param name: Name of the branch
        :return: AsyncBranch
        '''
        if name not in self._branch_map:
            self.get_logger().error("Branch {0} could not be found".format(name))
            return None

        return self._branch_map[name]

    def inherit(self, other_stream):
        '''
        Copy data from an other stream to this stream

        :param other_stream: Stream
        :return: None
        '''
        self._resource_map = other_stream._resource_map

    def append_node(self, node):
        '''
        Add a node to the stream queue

        :param node: Node
        :return: Stream
        '''
        self._nodes.append(node)
        return self

    def add_resource(self, res):
        '''
        Adds a resource to the stream

        :param res: Resource
        :return: Stream
        '''
        if res.get_prefix() in self._resource_map:
            self._resource_map[res.get_prefix()].append(res)
        else:
            self._resource_map[res.get_prefix()] = [res]

        res._stream = self
        return self

    def remove_resource(self, query):
        '''
        Find resources by query and remove them from the stream

        :param query: str
        :return: Stream
        '''
        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, name) = query.split(":")  # type: (str, str)

        if not prefix in self._resource_map:
            return

        for i in range(0, len(self._resource_map[prefix])):
            if self._resource_map[prefix][i].get_name() == name:
                self._resource_map[prefix].pop(i)

        return self

    def get_resource_by_name(self, name):
        '''
        Tries to find a resource by name and returns it

        :param name: Name of the resource
        :return: Resource
        '''

        for prefix, res in self._resource_map.items():
            for r in res:
                if r.get_name() == name:
                    return r

        return None

    def get_resources(self, query):
        '''
        Get one or more resources from the stream, using given query string

        :param query: str
        :return: list
        '''

        if query.find(":") == -1:
            if query == '*':
                # return all
                result_all = []
                for val in self._resource_map.values():
                    if isinstance(val, list):
                        result_all += val
                    else:
                        result_all.append(val)

                return result_all
            else:
                raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, key) = query.split(":")  # type: (str, str)

        if not prefix in self._resource_map:
            return []

        if key == "*":
            # return all
            return self._resource_map[prefix]

        # for all other queries we will traverse the resources and add them to our result list
        results = []

        for resource in self._resource_map[prefix]:
            # check if additional value is requested or whole resource
            requestedVal = None
            if key.find(".") > -1:
                requestedVal = key[key.find(".") + 1:]
                key = key[0:key.find(".")]

            # find one resource by name
            if key.find("*") == -1 and resource.get_name() == key:
                if requestedVal is None:
                    return [resource]
                else:
                    return resource.get_property(requestedVal)
            elif (key.startswith("*") and resource.get_name().endswith(key[1:])) or \
                    (key.endswith("*") and resource.get_name().startswith(key[0:-1])):

                if requestedVal is None:
                    results.append(resource)
                else:
                    results.append(resource.get_property(requestedVal))

        return results

    def flow(self):
        '''
        Starts the stream processing

        :return: bool - If false, errors have occured while processing the stream
        '''
        self.get_logger().info("Starting processing")
        self.fire_event(self.EVENT_STREAM_STARTED)
        nodes_processed = 0

        for node in self._nodes:
            if isinstance(node, AsyncBranch):
                self.get_logger().info("Starting new branch {0}".format(node.get_name()))
                node.get_stream().inherit(self)
                node.start()
            else:
                self.get_logger().debug("Running node {0}".format(node.__class__.__name__))
                self.fire_event(self.EVENT_NODE_STARTED)
                res = node.run(self)
                nodes_processed += 1
                self.fire_event(self.EVENT_NODE_FINISHED)

                if res is False:
                    self.get_logger().warning("Node failed.")
                    self.get_logger().info(
                        "Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
                    self.fire_event(self.EVENT_STREAM_FINISHED)

                    return False

        self.get_logger().info("Finished processing {0}/{1} nodes".format(nodes_processed, len(self._nodes)))
        self.fire_event(self.EVENT_STREAM_FINISHED)
        return True
