#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.properties import Property

__all__ = []


class InsertWorkflowNode(Node):
    """
    @Name: Insert workflow
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'workflow': Property(expected_type=Workflow, required=True, label='Workflow',
                                 hint='Select existing workflow')
        }

        super().__init__(node_properties, properties)

    def run(self, ctx) -> bool:
        super().run(ctx)

        return self.property('workflow').value().run()
