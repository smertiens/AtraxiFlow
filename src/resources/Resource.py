from common.PropertyObject import PropertyObject


class Resource (PropertyObject):

    def getName(self):
        return self.name;

    def getPrefix(self):
        raise Exception("Resources must overwrite getPrefix()")

    def getData(self, key):
        return self.getProperty(key, None)

    def __init__(self, name = "", props = {}):
        self.name = name
        self._user_properties = props
        self.properties = {}

    def getNodeClass(self):
        return "STUB"

