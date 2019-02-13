#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
from atraxiflow.common.events import EventObject

class PropertyObject(EventObject):

    EVENT_PROPERTY_CHANGED = 'property_changed'
    EVENT_PROPERTIES_CHECKED = 'properties_checked'

    def check_properties(self):

        # check if a primary property is used
        if type(self.properties) is not dict:
            foundMatch = False
            for name, opt in self._known_properties.items():
                if ("primary" in opt) and (opt["primary"] is True):
                    self.properties = dict([(name, self.properties)])
                    #self.fire_event(self.EVENT_PROPERTY_CHANGED, name)
                    foundMatch = True

            if foundMatch is not True:
                logging.error("Single argument given, but no primary property defined that will take it.")
                self.fire_event(self.EVENT_PROPERTIES_CHECKED, False)
                return False

        # check and merge properties
        for name, opt in self._known_properties.items():
            if ("required" in opt and opt["required"] is True) and (name not in self.properties):
                logging.error("Missing property: {0} in {1}".format(name, self.__class__.__name__))
                self.fire_event(self.EVENT_PROPERTIES_CHECKED, False)
                return False

            elif (name not in self.properties) and ("default" in opt):
                self.properties[name] = opt['default']
                #self.fire_event(self.EVENT_PROPERTY_CHANGED, name)

            elif name in self.properties:
                # this will fire when property has been set via the constructor's prop-argument
                #self.fire_event(self.EVENT_PROPERTY_CHANGED, name)
                pass

        self.fire_event(self.EVENT_PROPERTIES_CHECKED, True)
        return True

    def set_property(self, key, value):
        self.properties[key] = value
        self.fire_event(self.EVENT_PROPERTY_CHANGED, key)
        return self

    def get_property(self, key, default=""):
        if not key in self.properties:
            return default
        else:
            return self.properties[key]

    def get_known_properties(self):
        return self._known_properties


