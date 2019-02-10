import os

class FSObject:

    path = ""

    def __init__(self, new_path = ""):
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
        return os.path.splitext(self.path)[1]

    def getDirectory(self):
        return os.path.dirname(self.path)

    def getAbsolutePath(self):
        return os.path.realpath(self.path)

    def getBasename(self):
        return os.path.basename(self.path)