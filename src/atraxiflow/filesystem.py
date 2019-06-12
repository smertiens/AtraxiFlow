#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
from datetime import datetime


class FSObject:
    def __init__(self, new_path: str =''):
        self.path = new_path

    def __str__(self):
        return self.path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def isFile(self) -> bool:
        return os.path.isfile(self.path)

    def isFolder(self) -> bool:
        return os.path.isdir(self.path)

    def isSymlink(self) -> bool:
        return os.path.islink(self.path)

    def getFilename(self) -> str:
        return os.path.basename(self.path)

    def getExtension(self) -> str:
        ext = os.path.splitext(self.path)[1]

        # remove leading .
        if ext[0:1] == '.':
            ext = ext[1:]

        return ext

    def getDirectory(self) -> str:
        return os.path.dirname(self.path)

    def getAbsolutePath(self) -> str:
        return os.path.realpath(self.path)

    def getBasename(self) -> str:
        return os.path.splitext(self.getFilename())[0]

    def getFilesize(self) -> int:
        return os.path.getsize(self.path)

    def getLastModified(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    def getLastAccessed(self) -> datetime:
        return datetime.fromtimestamp(os.path.getatime(self.path))

    def getCreated(self) -> datetime:
        return datetime.fromtimestamp(os.path.getctime(self.path))
