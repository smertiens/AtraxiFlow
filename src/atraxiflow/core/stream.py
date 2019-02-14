#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
from threading import Thread

from atraxiflow.core.exceptions import ResourceException
from atraxiflow.nodes.foundation import Node, Resource


def flow():
    return 'flow'


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
        logging.info("Starting new thread on branch {0}".format(self.get_name()))
        return self.stream.flow()


class Stream:
    '''
    The main building block of a workflow. Streams hold all nodes and resources
    '''

    def __init__(self):
        self._resource_map = {}
        self._branch_map = {}
        self._nodes = []

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
            logging.error("Branch {0} could not be found".format(name))
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
        logging.info("Starting processing")

        for node in self._nodes:
            if isinstance(node, AsyncBranch):
                logging.info("Starting new branch {0}".format(node.get_name()))
                node.get_stream().inherit(self)
                node.start()
            else:
                logging.debug("Running node {0}".format(node.__class__.__name__))
                if node.run(self) is False:
                    return False

        logging.info("Finished processing {0} nodes".format(len(self._nodes)))
        return True
