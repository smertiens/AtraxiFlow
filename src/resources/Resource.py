from PropertyObject import PropertyObject


class Resource (PropertyObject):

    def getName(self):
        return self.name;

    def getPrefix(self):
        raise Exception("Resources must overwrite getPrefix()")

    def getData(self, key):
        return self.getProperty(key, None)

    def __init__(self, name = "", properties = {}):
        self.name = name
        self.properties = properties

