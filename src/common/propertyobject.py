import logging


class PropertyObject:

    def check_properties(self):

        # check if a primary property is used
        if type(self.properties) is not dict:
            foundMatch = False
            for name, opt in self._known_properties.items():
                if ("primary" in opt) and (opt["primary"] is True):
                    self.properties = dict([(name, self.properties)])
                    foundMatch = True

            if foundMatch is not True:
                logging.error("Single argument given, but no primary property defined that will take it.")
                return False

        # check and merge properties
        for name, opt in self._known_properties.items():
            if ("required" in opt and opt["required"] is True) and (name not in self.properties):
                logging.error("Missing property: {0} in {1}".format(name, self.__class__.__name__))
                return False

            elif (name not in self.properties) and ("default" in opt):
                self.properties[name] = opt['default']

        return True

    def set_property(self, key, value):
        self.properties[key] = value

    def get_property(self, key, default=""):
        if not key in self.properties:
            return default
        else:
            return self.properties[key]

    def get_known_properties(self):
        return self._known_properties
