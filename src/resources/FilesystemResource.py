from resources.Resource import *

class FilesystemResource(Resource):
    
    type = 'FilesystemResource'
    path = ''

    def __init__(self, new_path):
        self.path = new_path

    def getPath(self):
        return self.path