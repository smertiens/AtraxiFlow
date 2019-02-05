from resources.ResourceException import ResourceException
import logging

class Stream:

    _resources = []
    _resource_map = {}
    _nodes = []

    def appendNode(self, node):
        self._nodes.append(node)

    def registerResource(self, prefix, resourceClass):
        if not prefix in self._resource_map:
            self._resource_map[prefix] = resourceClass
        else:
            if self._resource_map[prefix] == resourceClass:
                raise ResourceException("Prefix '{0}' is already registered with an other resource".format(prefix))

    def addResource(self, res):
        if res.getPrefix() in self._resource_map:
            self._resource_map[res.getPrefix()].append(res)
        else:
            self._resource_map[res.getPrefix()] = [res]
    
    def removeResource(self, query):

        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, name) = query.split(":")  # type: (str, str)

        if not prefix in self._resource_map:
            return

        for i in range(0, len(self._resource_map[prefix])):
            if self._resource_map[prefix][i].getName() == name:
                self._resource_map[prefix].pop(i)



    def getResource(self, query):

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
            if key.find("*") == -1 and resource.getName() == key:
                if requestedVal is None:
                    return resource
                else:
                    return resource.getData(requestedVal)
            elif (key.startswith("*") and resource.getName().endswith(key[1:])) or \
                    (key.endswith("*") and resource.getName().startswith(key[0:-1])):

                if requestedVal is None:
                    results.append(resource)
                else:
                    results.append(resource.getData(requestedVal))

        return results

    def run(self):
        logging.info("Starting processing")

        for node in self._nodes:
            self._runNode(node)

        logging.info("Finished processing {0} nodes".format(len(self._nodes)))

    def _runNode (self, node):
        logging.info("Running {0}".format(node.getNodeClass()))
        node.run(self)

        # Run child nodes
        for child in node.children:
            self._runNode(child)