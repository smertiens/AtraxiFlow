class Resource:

    def getName(self):
        return self.name;

    def getPrefix(self):
        raise Exception("Resources must overwrite getPrefix()")

    def getData(self, key):
        return self.getProperty(key, None)

    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key, default = ""):
        if not key in self.properties:
            return default
        else:
            return self.properties[key]

    def __init__(self, name = "", properties = {}):
        self.name = name
        self.properties = properties

