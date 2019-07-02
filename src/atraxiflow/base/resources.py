#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os
from datetime import datetime
from atraxiflow.core import Resource


class TextResource(Resource):
    '''
    A resource holding a text
    '''

    def __init__(self, value: str):
        self._value = value
        self.id = '%s.%s' % ('atraxiflow', self.__class__.__name__)


class FilesystemResource(Resource):

    def __init__(self, new_path: str = ''):
        self.id = '%s.%s' % ('atraxiflow', self.__class__.__name__)
        self.path = new_path

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.__str__()

    def get_value(self) -> str:
        return self.path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def is_file(self) -> bool:
        return os.path.isfile(self.path)

    def is_folder(self) -> bool:
        return os.path.isdir(self.path)

    def is_symlink(self) -> bool:
        return os.path.islink(self.path)

    def get_filename(self) -> str:
        return os.path.basename(self.path)

    def get_extension(self) -> str:
        ext = os.path.splitext(self.path)[1]

        # remove leading .
        if ext[0:1] == '.':
            ext = ext[1:]

        return ext

    def get_directory(self) -> str:
        return os.path.dirname(self.path)

    def get_absolute_path(self) -> str:
        return os.path.realpath(self.path)

    def get_basename(self) -> str:
        return os.path.splitext(self.get_filename())[0]

    def get_filesize(self) -> int:
        return os.path.getsize(self.path)

    def get_last_modified(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    def get_last_accessed(self) -> datetime:
        return datetime.fromtimestamp(os.path.getatime(self.path))

    def get_created(self) -> datetime:
        return datetime.fromtimestamp(os.path.getctime(self.path))
