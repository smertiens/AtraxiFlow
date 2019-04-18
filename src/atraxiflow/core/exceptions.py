#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

__all__ = ['ResourceException', 'EnvironmentException', 'ValueException', 'ExecutionException', 'FilesystemException',
           'GUIException', 'PropertyException', 'InputException']


class ResourceException(Exception):
    pass


class EnvironmentException(Exception):
    pass


class ValueException(Exception):
    pass


class ExecutionException(Exception):
    pass


class FilesystemException(Exception):
    pass


class GUIException(Exception):
    pass


class PropertyException(Exception):
    pass


class InputException(Exception):
    pass
