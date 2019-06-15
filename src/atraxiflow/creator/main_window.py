#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from PySide2 import QtCore, QtWidgets, QtGui
from atraxiflow.creator.widgets import AxNodeWidget, AxNodeWidgetContainer
from atraxiflow.base.filesystem import *
from atraxiflow.core import Node
from atraxiflow.creator.models import AxNodeTreeModel


class CreatorMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.workflow_ctx = WorkflowContext()
        self.setWindowTitle('AtraxiFlow - Creator')

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout())

        # Tab bar
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)

        # Main toolbar
        main_toolbar = QtWidgets.QToolBar()
        main_toolbar.setOrientation(QtCore.Qt.Vertical)

        action_new = QtWidgets.QAction('N', main_toolbar)
        action_open = QtWidgets.QAction('O', main_toolbar)
        action_save = QtWidgets.QAction('S', main_toolbar)

        main_toolbar.addAction(action_new)
        main_toolbar.addAction(action_open)
        main_toolbar.addAction(action_save)
        main_toolbar.addSeparator()

        # Statusbar
        self.status_bar = QtWidgets.QStatusBar()

        # Node list
        node_tree_layout = QtWidgets.QVBoxLayout()
        node_tree_layout.setSpacing(0)

        tree_query_input = QtWidgets.QLineEdit()
        tree_query_input.setPlaceholderText('Filter nodes...')
        tree_query_input.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.load_node_tree(s))
        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.connect(QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*, int)'),
                               lambda i, c: self.add_node_to_current_workspace(i.data(c, QtCore.Qt.UserRole)))
        self.node_tree.setHeaderHidden(True)
        node_tree_layout.addWidget(tree_query_input)
        node_tree_layout.addWidget(self.node_tree)

        # Add widgets to window
        central_widget.layout().addLayout(node_tree_layout)
        central_widget.layout().addWidget(self.tab_bar)

        self.addToolBar(QtCore.Qt.LeftToolBarArea, main_toolbar)
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

        # Create default tab
        self.tab_bar.addTab(self.create_workflow_tab(), 'Default Workflow')

        self.load_node_tree()

        self.resize(1024, 800)

    def add_node_to_current_workspace(self, node):
        wrapper = self.tab_bar.currentWidget().widget()
        node = self.create_node_widget(node(), wrapper)
        node.move(0, 0)
        wrapper.discover_nodes()

    def load_node_tree(self, filter: str = None):

        def iter_nodes(parent_item, nodes, filter=None):
            for node in nodes:
                if filter is not None:
                    if not filter.lower() in node.__name__.lower():
                        continue

                node_item = QtWidgets.QTreeWidgetItem()
                node_item.setText(0, node.__name__)
                node_item.setData(0, QtCore.Qt.UserRole, node)
                parent_item.addChild(node_item)

            return parent_item

        self.node_tree.clear()

        for group, nodes in self.workflow_ctx.get_nodes().items():
            group_item = QtWidgets.QTreeWidgetItem()
            group_item.setText(0, group)

            if isinstance(nodes, dict):
                for subgroup, nodes_2 in nodes.items():
                    subgroup_item = QtWidgets.QTreeWidgetItem()
                    subgroup_item.setText(0, subgroup)
                    subgroup_item = iter_nodes(subgroup_item, nodes_2, filter)
                    group_item.addChild(subgroup_item)

            elif isinstance(nodes, list):
                group_item = iter_nodes(group_item, nodes, filter)

            self.node_tree.insertTopLevelItem(0, group_item)
            self.node_tree.expandAll()

    def create_node_widget(self, node: Node, parent: AxNodeWidgetContainer):
        return AxNodeWidget(node, parent)

    def create_workflow_tab(self, title=''):
        scroll_area = QtWidgets.QScrollArea()
        wrapper = AxNodeWidgetContainer()
        scroll_area.setWidget(wrapper)
        wrapper.resize(scroll_area.width(), scroll_area.height())

        return scroll_area
