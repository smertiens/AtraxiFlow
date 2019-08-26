#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import uuid

from PySide2 import QtWidgets, QtCore

from atraxiflow.core import *
from atraxiflow.properties import *


class WorkflowNode(Node):
    """
    @Name: Workflow
    """

    def __init__(self, properties=None):
        node_properties = {
            'name': Property(expected_type=str, required=False, hint='The id of your workflow', label='Name',
                             default='Workflow', display_options={'hide_in_ui': True})
        }
        super().__init__(node_properties, properties)

        # internal id
        self.id = str(uuid.uuid4())

    def get_id(self) -> str:
        return self.id

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        return True
