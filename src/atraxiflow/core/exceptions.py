#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


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