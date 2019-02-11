from resources.Resource import *
from common.FSObject import FSObject

import glob, logging

"""
Provides access to the filesysmtem.

Properties:
    sourcePattern - a qualified a qualified path to a file folder, can include wildcards 
"""
class FilesystemResource(Resource):
    
    type = 'FilesystemResource'
    _known_properties = {
        'sourcePattern': {
            'label': "Source",
            'type': "file",
            'required': True,
            'hint': 'A file or folder',
            'default': '',
            'primary': True
        }
    }
    _fsobjects = []
    _resolved = False

    def getPrefix(self):
        return 'FS'

    def _resolve(self):
        if self._resolved:
            return

        items = glob.glob(self.getProperty("sourcePattern"))
        self._fsobjects.clear()

        for item in items:
            self._fsobjects.append(FSObject(item))

        self._resolved = True

    def removeData(self, obj):
        if obj not in self._fsobjects:
            logging.error("Cannot remove: {0}, not found in this resource".format(obj))
            return

        self._fsobjects.remove(obj)

    def getData(self, key = ""):
        self.mergeProperties()

        if "" == key:
            self._resolve()
            return self._fsobjects
        else:
            return self.getProperty(key)

