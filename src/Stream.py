from resources.ResourceException import ResourceException

class Stream:

    resources = []
    resource_map = {}

    def registerResource(self, prefix, resourceClass):
        if not prefix in self.resource_map:
            self.resource_map[prefix] = resourceClass
        else:
            if self.resource_map[prefix] == resourceClass:
                raise ResourceException("Prefix '{0}' is already registered with an other resource".format(prefix))

    def addResource(self, res):
        if res.getPrefix() in self.resource_map:
            self.resource_map[res.getPrefix()].append(res)
        else:
            self.resource_map[res.getPrefix()] = [res]
    
    def removeResource(self, query):

        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))

        (prefix, name) = query.split(":")  # type: (str, str)

        if not prefix in self.resource_map:
            return

        for i in range(0, len(self.resource_map[prefix])):
            if self.resource_map[prefix][i].getName() == name:
                self.resource_map[prefix].pop(i)



    def getResource(self, query):

        if query.find(":") == -1:
            raise ResourceException("Invalid resource identifier '{0}'. Should be Prefix:Name".format(query))


        (prefix, key) = query.split(":")  # type: (str, str)

        if not prefix in self.resource_map:
            return []

        if key == "*":
            # return all
            return self.resource_map[prefix]


        # for all other queries we will traverse the resources and add them to our result list
        results = []

        for resource in self.resource_map[prefix]:
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


    def getResources(self, type = ''):
        if (type == ''):
            return self.resources
        else:
            result = []

            for res in self.resources:
                if (res.type == type):
                    result.append(res)
            
            return result

