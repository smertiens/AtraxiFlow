#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from nodes.foundation import Resource
from common.graphics import ImageObject
from common.propertyobject import PropertyObject
import logging

class ImageResource(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'src': {
                'label': "Source",
                'type': "file,image",
                'required': True,
                'hint': 'An image file or object',
                'default': '',
                'primary': True
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

        # node specific
        self._imgobject = None

        self.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self._ev_property_changed)
        self.add_listener(PropertyObject.EVENT_PROPERTIES_CHECKED, self._ev_properties_checked)

    def _process_src(self):
        # do not process src again if imgobject is set
        # otherwise changes made by processing nodes would be overwritten
        if self._imgobject is not None:
            return

        if isinstance(self.get_property('src'), ImageObject):
            self._imgobject = self.get_property('src')
        else:
            self._imgobject = ImageObject(self.get_property('src'))

    def _ev_property_changed(self, data):
        if data == 'src':
            self._process_src()

    def _ev_properties_checked(self, data):
        if data is True:
            self._process_src()

    def get_prefix(self):
        return 'Img'

    def remove_data(self, obj):
        self._imgobject = None

    def get_data(self):
        self.check_properties()
        return self._imgobject

    def update_data(self, data):
        if not isinstance(data, ImageObject):
            logging.error("Expected ImageObject, got {0}".format(type(data)))
            return

        self._imgobject = data
