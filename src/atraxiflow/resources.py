#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import glob

from atraxiflow.core import Resource
from atraxiflow.filesystem import FSObject
from typing import List

class TextResource(Resource):
    '''
    A resource holding a text
    '''

    def __init__(self, value: str):
        self._value = value
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)


class FilesystemResource(Resource):
    """
    Provides access to the filesystem.
    """

    def __init__(self, path: str):
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._fsobjects = []
        items = glob.glob(path)

        for item in items:
            self._fsobjects.append(FSObject(item))

    def get_value(self) -> List[FSObject]:
        return self._fsobjects

    def __str__(self):
        lines = ['\t' + str(x) for x in self._fsobjects]
        lines.insert(0, 'FilesystemResource:')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()
