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
from atraxiflow.creator import assets, tasks
import logging


class CreatorMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.workflow_ctx = WorkflowContext()
        self.setWindowTitle('AtraxiFlow - Creator')

        logging.getLogger('creator').debug('Building main window...')

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout())
        central_widget.layout().setSpacing(0)

        # Tab bar
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)

        # Main menu
        menu_bar = QtWidgets.QMenuBar()
        file_menu = QtWidgets.QMenu('&File')
        menu_file_quit = QtWidgets.QAction('Quit', file_menu)
        wf_menu = QtWidgets.QMenu('&Workflow')
        menu_wf_run = QtWidgets.QAction('Run', wf_menu)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(wf_menu)

        # Main toolbar
        main_toolbar = QtWidgets.QToolBar()

        self.action_play = QtWidgets.QAction('Play', main_toolbar)
        self.action_play.setIcon(QtGui.QIcon(assets.get_asset('icons8-play-50.png')))
        self.action_play.connect(QtCore.SIGNAL('triggered()'), self.run_active_workflow)
        self.action_stop = QtWidgets.QAction('Stop', main_toolbar)
        self.action_stop.setIcon(QtGui.QIcon(assets.get_asset('icons8-stop-50.png')))
        self.action_stop.setEnabled(False)

        main_toolbar.addAction(self.action_play)
        main_toolbar.addAction(self.action_stop)
        dock_main_toolbar = QtWidgets.QDockWidget()
        dock_main_toolbar.setWindowTitle('Controls')
        dock_main_toolbar.setWidget(main_toolbar)

        # Statusbar
        self.status_bar = QtWidgets.QStatusBar()

        # Node list
        node_tree_wrapper = QtWidgets.QWidget()
        node_tree_wrapper.setLayout(QtWidgets.QVBoxLayout())
        node_tree_wrapper.layout().setSpacing(0)

        tree_query_input = QtWidgets.QLineEdit()
        tree_query_input.setPlaceholderText('Filter nodes...')
        tree_query_input.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.load_node_tree(s))
        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.connect(QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*, int)'),
                               lambda i, c: self.add_node_to_current_workspace(i.data(c, QtCore.Qt.UserRole)))
        self.node_tree.setHeaderHidden(True)
        node_tree_wrapper.layout().addWidget(tree_query_input)
        node_tree_wrapper.layout().addWidget(self.node_tree)
        dock_node_tree = QtWidgets.QDockWidget()
        dock_node_tree.setWindowTitle('Nodes')
        dock_node_tree.setWidget(node_tree_wrapper)

        # Add data tree
        self.data_tree = QtWidgets.QTreeWidget()
        self.data_tree.setColumnCount(2)

        dock_data_tree = QtWidgets.QDockWidget()
        dock_data_tree.setWindowTitle('Data')
        dock_data_tree.setWidget(self.data_tree)

        # Add widgets to window
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_data_tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_node_tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_main_toolbar)

        central_widget.layout().addWidget(self.tab_bar)
        # self.addToolBar(QtCore.Qt.LeftToolBarArea, main_toolbar)
        self.setMenuBar(menu_bar)
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

        # Create default tab
        self.tab_bar.addTab(self.create_workflow_tab(), 'Default Workflow')

        logging.getLogger('creator').debug('Loading nodes...')
        self.load_node_tree()

        self.resize(1024, 800)

    def run_active_workflow(self):
        node_container = self.tab_bar.currentWidget().widget()
        assert isinstance(node_container, AxNodeWidgetContainer)

        selected_node = node_container.get_selected_node()
        if selected_node is not None:
            root_node = node_container.get_root_node(selected_node)
            ax_nodes = node_container.extract_node_hierarchy_from_widgets(root_node)

            run_task = tasks.RunWorkflowTask(ax_nodes)
            run_task.set_on_finish(self.run_finished)
            run_task.get_workflow().add_listener(Workflow.EVENT_NODE_RUN_FINISHED, self.node_run_finished)

            self.data_tree.clear()
            self.action_play.setEnabled(False)
            self.action_stop.setEnabled(True)
            
            run_task.start()

    def node_run_finished(self, data):
        node = data['node']
        assert isinstance(node, Node)

        node_item = QtWidgets.QTreeWidgetItem()
        node_item.setText(0, node.get_name())
        inputs = QtWidgets.QTreeWidgetItem()

        # Update data tree with current node
        if not node.has_input() or node.get_input().size() == 0:
            inputs.setText(0, 'Inputs: None')
        else:
            inputs.setText(0, 'Inputs')

            for inp in node.get_input().items():
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, inp.__class__.__name__)
                item.setText(1, str(inp))

                inputs.addChild(item)

        outputs = QtWidgets.QTreeWidgetItem()

        if node.get_output() is None or node.get_output().size() == 0:
            outputs.setText(0, 'Output: None')
        else:
            outputs.setText(0, 'Output')

            for outp in node.get_output().items():
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, outp.__class__.__name__)
                item.setText(1, str(outp))
                outputs.addChild(item)

        node_item.addChild(inputs)
        inputs.setExpanded(True)
        node_item.addChild(outputs)
        outputs.setExpanded(True)

        self.data_tree.insertTopLevelItem(self.data_tree.topLevelItemCount(), node_item)
        node_item.setExpanded(True)

    def run_finished(self, task: tasks.RunWorkflowTask):
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(False)

    def add_node_to_current_workspace(self, node):
        wrapper = self.tab_bar.currentWidget().widget()
        ui_node = self.create_node_widget(node(), wrapper)
        ui_node.move(10, 10)
        ui_node.show()

        wrapper.discover_nodes()

    def load_node_tree(self, filter: str = None):

        def iter_nodes(parent_item, nodes, filter=None):
            for node in nodes:
                if filter is not None:
                    if not filter.lower() in node.__name__.lower():
                        continue

                node_item = QtWidgets.QTreeWidgetItem()
                node_item.setText(0, node.get_name() if node.get_name() != '' else str(node.__name__))
                node_item.setData(0, QtCore.Qt.UserRole, node)
                node_item.setIcon(0, QtGui.QIcon(assets.get_asset('icons8-box-50.png')))
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
