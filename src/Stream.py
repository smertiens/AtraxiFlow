from exceptions import ResourceException
import logging


class Stream:
    def __init__(self):
        self._resources = []
        self._resource_map = {}
        self._nodes = []

    def append_node(self, node):
        self._nodes.append(node)

    def register_resource(self, prefix, resourceClass):
        if not prefix in self._resource_map:
            self._resource_map[prefix] = resourceClass
        else:
            if self._resource_map[prefix] == resourceClass:
                raise ResourceException("Prefix '{0}' is already registered with an other resource".format(prefix))

    def add_resource(self, res):
        if res.get_prefix() in self._resource_map:
            self._resource_map[res.get_prefix()].append(res)
        else:
            self._resource_map[res.get_prefix()] = [res]

    def remove_resource(self, query):

        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, name) = query.split(":")  # type: (str, str)

        if not prefix in self._resource_map:
            return

        for i in range(0, len(self._resource_map[prefix])):
            if self._resource_map[prefix][i].get_name() == name:
                self._resource_map[prefix].pop(i)

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
                    return resource.get_data(requestedVal)
            elif (key.startswith("*") and resource.get_name().endswith(key[1:])) or \
                    (key.endswith("*") and resource.get_name().startswith(key[0:-1])):

                if requestedVal is None:
                    results.append(resource)
                else:
                    results.append(resource.get_data(requestedVal))

        return results

    def run(self):
        logging.info("Starting processing")

        for node in self._nodes:
            if self._run_node(node) is False:
                return False

        logging.info("Finished processing {0} nodes".format(len(self._nodes)))
        return True

    def _run_node(self, node):
        logging.info("Running {0}".format(node.__class__.__name__))
        if node.run(self) is False:
            logging.error('Error processing node. Exiting.')
            return False

        # Run child nodes
        for child in node.children:
            self._run_node(child)

        return True
