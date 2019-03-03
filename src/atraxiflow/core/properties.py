#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging

from atraxiflow.core.events import EventObject
from atraxiflow.core.exceptions import *

class PropertyObject(EventObject):
    EVENT_PROPERTY_CHANGED = 'property_changed'
    EVENT_PROPERTIES_CHECKED = 'properties_checked'

    def check_properties(self):
        '''
        Check and merge properties

        :return: boolean
        '''

        for name, opt in self._known_properties.items():
            if ("required" in opt and opt["required"] is True) and (name not in self.properties):
                self.fire_event(self.EVENT_PROPERTIES_CHECKED, False)
                raise PropertyException("Missing property: {0} in {1}".format(name, self.__class__.__name__))

            elif (name not in self.properties) and ("default" in opt):
                self.properties[name] = opt['default']

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

    def get_properties_from_args(self, arg1, arg2):
        '''
        Will check if the first argument is a string or a dict. If its a string we assume
        it is the node name, if its a dict we will return it as properties.

        :param arg1:
        :param arg2:
        :return: tuple
        '''

        name = ""
        props = {}
        if isinstance(arg1, str):
            name = arg1

            if isinstance(arg2, dict):
                props = arg2

        elif isinstance(arg1, dict):
            props = arg1

        return tuple([name, props])
