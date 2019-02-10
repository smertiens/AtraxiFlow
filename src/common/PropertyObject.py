import logging

class PropertyObject:

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


    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key, default=""):
        if not key in self.properties:
            return default
        else:
            return self.properties[key]


    def getKnownProperties(self):
        return self._known_properties