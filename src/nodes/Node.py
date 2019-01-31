import logging

class Node:

    children = []
    properties = {}
    _known_properties = {}
    hasErrors = False

    def getNodeType(self):
        raise Exception("Node class must implement getNodeType-method")

    def setProperty(self, key, value):
        self.properties[key] = value
    
    def getProperty(self, key):
        if not key in self.properties:
            return None
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
                logging.error("Missing property: " + name + " in " + self.getNodeType())
                self.hasErrors = True
                continue
            
            if (not name in self.properties):
                self.setProperty(name, opt['default'])


    def __init__(self, props = {}):
        self.properties = props

    def run(self, stream):
        raise Exception("Node class must implement run-method")