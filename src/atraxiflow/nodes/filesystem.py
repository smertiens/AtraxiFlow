#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.properties import *
from atraxiflow.resources import FilesystemResource

class LoadFilesNode(Node):

    def __init__(self, properties: dict):
        self.output = Container()
        self.properties = {
            'path': Property(expected_type=str, required=True)
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext):
        self.output = Container(FilesystemResource(self.property('path').value()))
