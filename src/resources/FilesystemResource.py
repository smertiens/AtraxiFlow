from resources.Resource import *
from common.FSObject import FSObject

import glob

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
            'default': ''
        }
    }
    _fsobjects = []

    def getPrefix(self):
        return 'FS'

    def _resolve(self):
        items = glob.glob(self.getProperty("sourcePattern"))

        for item in items:
            self._fsobjects.append(FSObject(item))


    def getData(self, key = ""):
        if "" == key:
            self._resolve()
            return self._fsobjects
        else:
            return self.getProperty(key)

