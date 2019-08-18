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
                             default='Workflow')
        }
        super().__init__(node_properties, properties)

        # internal id
        self.id = str(uuid.uuid4())

    def get_id(self) -> str:
        return self.id

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        return True

    def get_ui(self, node_widget) -> QtWidgets.QWidget:
        node_widget.setObjectName('__creator_workflow_widget')

        w = QtWidgets.QWidget()
        w.setLayout(QtWidgets.QHBoxLayout())

        self.input_name = QtWidgets.QLineEdit()
        self.input_name.setObjectName('__creator_workflow_widget_name_input')
        self.input_name.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.property('name').set_value(s))
        w.layout().addWidget(self.input_name)

        return w

    def load_ui_data(self):
        self.input_name.setText(self.property('name').value())

    def apply_ui_data(self):
        self.property('name').set_value(self.input_name.text())
