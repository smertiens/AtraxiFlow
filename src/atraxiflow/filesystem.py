#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
from datetime import datetime

from atraxiflow.core import Container
class FSObject:
    def __init__(self, new_path=""):
        self.path = new_path

    def __str__(self):
        return self.path

    def exists(self):
        return os.path.exists(self.path)

    def isFile(self):
        return os.path.isfile(self.path)

    def isFolder(self):
        return os.path.isdir(self.path)

    def isSymlink(self):
        return os.path.islink(self.path)

    def getFilename(self):
        return os.path.basename(self.path)

    def getExtension(self):
        ext = os.path.splitext(self.path)[1]

        # remove leading .
        if ext[0:1] == '.':
            ext = ext[1:]

        return ext

    def getDirectory(self):
        return os.path.dirname(self.path)

    def getAbsolutePath(self):
        return os.path.realpath(self.path)

    def getBasename(self):
        return os.path.splitext(self.getFilename())[0]

    def getFilesize(self):
        return os.path.getsize(self.path)

    def getLastModified(self):
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    def getLastAccessed(self):
        return datetime.fromtimestamp(os.path.getatime(self.path))

    def getCreated(self):
        return datetime.fromtimestamp(os.path.getctime(self.path))
