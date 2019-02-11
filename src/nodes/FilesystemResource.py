from nodes.foundation import Resource
from common.filesystem import FSObject
from common.propertyobject import PropertyObject

import glob, logging

"""
Provides access to the filesysmtem.

Properties:
    sourcePattern - a qualified a qualified path to a file folder, can include wildcards 
"""


class FilesystemResource(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'sourcePattern': {
                'label': "Source",
                'type': "file",
                'required': True,
                'hint': 'A file or folder',
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
        self._fsobjects = []
        self._resolved = False

        # events
        self.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self.event_property_changed)

    def event_property_changed(self, data):
        if data == 'sourcePattern':
            self._resolved = False
            self._resolve()

    def get_prefix(self):
        return 'FS'

    def _resolve(self):
        if self._resolved:
            return

        items = glob.glob(self.get_property("sourcePattern"))
        self._fsobjects.clear()

        for item in items:
            self._fsobjects.append(FSObject(item))

        self._resolved = True

    def remove_data(self, obj):
        if obj not in self._fsobjects:
            logging.error("Cannot remove: {0}, not found in this resource".format(obj))
            return

        self._fsobjects.remove(obj)

    def get_data(self, key=""):
        self.check_properties()

        if "" == key:
            return self._fsobjects
        else:
            return self.get_property(key)
