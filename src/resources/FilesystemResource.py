from resources.Resource import *

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

    def getPrefix(self):
        return 'FS'

    def getData(self, key):
        # ignore key - we only hold one single resource, and that is a file/folder
        return self.getProperty("sourcePattern")

