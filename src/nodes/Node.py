import logging


class Node:

    def getName(self):
        return self.name

    def getNodeClass(self):
        raise Exception("Node class must implement getNodeType-method")

    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key, default=""):
        if not key in self.properties:
            return default
        else:
            return self.properties[key]

    def addChild(self, node):
        self.children.append(node)

    def removeChild(self, index):
        self.children.remove(index)

    def mergeProperties(self):
        # check if a primary property is used
        if type(self._user_properties) is not dict:
            foundMatch = False
            for name, opt in self._known_properties.items():
                if ("primary" in opt) and (opt["primary"] is True):
                    self._user_properties = dict([(name, self._user_properties)])
                    foundMatch = True

            if foundMatch is not True:
                logging.error("Single argument given, but no primary property defined that will take it.")
                self.hasErrors = True
                return

        # check and merge properties
        for name, opt in self._known_properties.items():
            if ("required" in opt and opt["required"] is True) and (name not in self._user_properties):
                logging.error("Missing property: {0} in {1}::{2}".format(name, self.getNodeClass(), self.getName()))
                self.hasErrors = True
                return
            elif name not in self._user_properties and "default" in opt:
                self.properties[name] = opt['default']
            else:
                self.properties[name] = self._user_properties[name]

    def __init__(self, name="", props=dict()):
        self.name = name
        self._user_properties = props
        self.properties = {}
        self.hasErrors = False

    def run(self, stream):
        raise Exception("Node class must implement run-method")
