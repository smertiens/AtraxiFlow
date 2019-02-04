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

    def checkProperties(self):
        # check for property integrity
        for name, opt in self._known_properties.items():

            if (opt['required'] == True) and (not name in self.properties):
                logging.error("Missing property: " + name + " in " + self.getNodeClass())
                self.hasErrors = True
                continue

            if (not name in self.properties) and "default" in opt:
                self.setProperty(name, opt['default'])

    def __init__(self, name="", props={}):
        self.name = name
        self.properties = props

    def run(self, stream):
        raise Exception("Node class must implement run-method")
