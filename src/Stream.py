#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from exceptions import ResourceException
import logging, copy
from threading import Thread

class AsyncBranch(Thread):

    def __init__(self, name, stream):
        super().__init__()

        self._nodes = []
        self.name = name
        self.stream = stream

    def set_stream(self, stream):
        self.stream = stream

    def get_stream(self):
        return self.stream

    def get_name(self):
        return  self.name

    def run(self):
        logging.info("Starting new thread on branch {0}".format(self.get_name()))
        return self.stream.run()


class Stream:
    def __init__(self):
        self._resource_map = {}
        self._branch_map = {}
        self._nodes = []

    def branch(self, name):
        branch = AsyncBranch(name, Stream())
        self.append_node(branch)
        self._branch_map[branch.get_name()] = branch
        return branch.get_stream()

    def get_branch(self, name):
        if name not in self._branch_map:
            logging.error("Branch {0} could not be found".format(name))
            return None

        return self._branch_map[name]

    def inherit(self, other_stream):
        self._resource_map = other_stream._resource_map

    def append_node(self, node):
        self._nodes.append(node)
        return self

    def add_resource(self, res):
        if res.get_prefix() in self._resource_map:
            self._resource_map[res.get_prefix()].append(res)
        else:
            self._resource_map[res.get_prefix()] = [res]

        return self

    def remove_resource(self, query):

        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, name) = query.split(":")  # type: (str, str)

        if not prefix in self._resource_map:
            return

        for i in range(0, len(self._resource_map[prefix])):
            if self._resource_map[prefix][i].get_name() == name:
                self._resource_map[prefix].pop(i)

        return self

    def get_resources(self, query):

        if query.find(":") == -1:
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
                    return resource
                else:
                    return resource.get_property(requestedVal)
            elif (key.startswith("*") and resource.get_name().endswith(key[1:])) or \
                    (key.endswith("*") and resource.get_name().startswith(key[0:-1])):

                if requestedVal is None:
                    results.append(resource)
                else:
                    results.append(resource.get_property(requestedVal))

        return results

    def run(self):
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
