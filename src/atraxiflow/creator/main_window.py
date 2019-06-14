#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from PySide2 import QtCore, QtWidgets, QtGui
from atraxiflow.creator.widgets import AxNodeWidget
from atraxiflow.base.filesystem import *
from atraxiflow.core import Node

class CreatorMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('AtraxiFlow - Creator')

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QVBoxLayout())

        # Tab bar
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)
        central_widget.layout().addWidget(self.tab_bar)

        # Statusbar
        self.status_bar = QtWidgets.QStatusBar()

        # Add widgets to window
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

        # Create default tab
        self.tab_bar.addTab(self.create_workflow_tab(), 'Default Workflow')

        self.resize(1024, 800)

    def create_node_widget(self, node: Node, parent: QtWidgets.QWidget):
        return AxNodeWidget(node, parent)

    def create_workflow_tab(self, title=''):
        scroll_area = QtWidgets.QScrollArea()
        wrapper = QtWidgets.QWidget()
        scroll_area.setWidget(wrapper)
        wrapper.resize(scroll_area.width(), scroll_area.height())

        node = self.create_node_widget(LoadFilesNode(), wrapper)
        node.move(20, 20)

        node2 = self.create_node_widget(FileFilterNode(), wrapper)
        node2.move(50, 50)

        return scroll_area
