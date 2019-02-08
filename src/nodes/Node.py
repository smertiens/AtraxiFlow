import logging

from PropertyObject import PropertyObject


class Node (PropertyObject):

    def getName(self):
        return self.name

    def getNodeClass(self):
        raise Exception("Node class must implement getNodeClass-method")


    def addChild(self, node):
        self.children.append(node)

    def removeChild(self, index):
        self.children.remove(index)


    def __init__(self, name="", props=dict()):
        self.name = name
        self._user_properties = props
        self.properties = {}
        self.hasErrors = False


    def run(self, stream):
        raise Exception("Node class must implement run-method")

