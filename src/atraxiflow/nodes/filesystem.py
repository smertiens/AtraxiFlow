#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import glob

from atraxiflow.core import *
from atraxiflow.properties import *
from atraxiflow.filesystem import FSObject

class FilesystemResource(Resource):
    """
    Provides access to the filesystem.
    """

    def __init__(self, path):
        self.id = '%s.%s' % (self.__module__, self.__class__)
        self._fsobjects = []
        items = glob.glob(path)
        for item in items:
            self._fsobjects.append(FSObject(item))

    def get_paths(self):
        return self._fsobjects

    def __str__(self):
        lines = ['\t' + str(x) for x in self._fsobjects]
        lines.insert(0, 'FilesystemResource:')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


class LoadFilesNode(Node):

    def __init__(self, properties):
        self.output = Container()
        self.properties = {
            'path': Property(expected_type=str, required=True)
        }
        self.id = '%s.%s' % (self.__module__, self.__class__)
        self._input = None

        self.apply_properties(properties)

    def run(self):
        self.output = Container(FilesystemResource(self.property('path').get()))
