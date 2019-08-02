#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import sys

from atraxiflow.base.filesystem import *
from atraxiflow.core import Node
from atraxiflow.creator import assets, tasks, wayfiles
from atraxiflow.creator.widgets import AxNodeWidget, AxNodeWidgetContainer, AxWorkflowWidget, AxNodeTreeWidget

__all__ = ['CreatorMainWindow']


class CreatorMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Context needed for pulling available nodes
        self.workflow_ctx = WorkflowContext()
        logging.getLogger('creator').debug('Building main window...')

        # Tab bar - displays the currently opened workflows
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.connect(QtCore.SIGNAL('tabCloseRequested(int)'), self.tab_closed)

        # Statusbar
        self.status_bar = QtWidgets.QStatusBar()
        self.status_label = QtWidgets.QLabel('Ready')
        self.status_label.setObjectName('status_label')
        self.status_bar.addWidget(self.status_label)

        # Splitter between node list and workflow area
        horiz_splitter = QtWidgets.QSplitter()
        self.node_list = AxNodeTreeWidget()  # self.create_node_list_widget()
        self.node_list.node_dbl_clicked.connect(self.add_node_to_current_workspace)
        horiz_splitter.addWidget(self.node_list)
        horiz_splitter.addWidget(self.tab_bar)

        # Splitter between node list/workflow area and data tree
        vertical_splitter = QtWidgets.QSplitter()
        vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        vertical_splitter.addWidget(horiz_splitter)
        self.data_list = self.create_data_tree_widget()
        vertical_splitter.addWidget(self.data_list)

        # Central widget - holds node tree, data tree and workflow area
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout())
        central_widget.layout().setSpacing(0)
        central_widget.layout().setContentsMargins(0, 0, 0, 0)
        central_widget.layout().addWidget(vertical_splitter)

        # Add components to main window
        self.setMenuBar(self.create_main_menu())
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

        # Setup window title, style and size/position
        self.setWindowTitle('AtraxiFlow - Creator')
        self.load_style()
        self.resize(1024, 800)

        # Create default tab with new, empty workflow
        self.create_workflow_tab()

        # Load available nodes to tree
        logging.getLogger('creator').debug('Loading nodes...')
        self.load_node_tree()

    def create_data_tree_widget(self) -> QtWidgets.QTreeWidget:
        data_tree = QtWidgets.QTreeWidget()
        data_tree.setColumnCount(1)
        data_tree.setHeaderHidden(True)
        data_tree.setObjectName('data_tree')
        return data_tree

    def create_node_list_widget(self) -> QtWidgets.QWidget:
        # Its a tree - also: create separate widget
        node_tree_wrapper = QtWidgets.QWidget()
        node_tree_wrapper.setLayout(QtWidgets.QVBoxLayout())
        node_tree_wrapper.layout().setSpacing(0)
        node_tree_wrapper.layout().setContentsMargins(0, 0, 0, 0)

        tree_query_input = QtWidgets.QLineEdit()
        tree_query_input.setObjectName('tree_query_input')
        tree_query_input.setPlaceholderText('Filter nodes...')
        tree_query_input.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.filter_node_tree(s))
        node_tree = QtWidgets.QTreeWidget()
        node_tree.setObjectName('node_tree')
        node_tree.connect(QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*, int)'),
                          lambda i, c: self.add_node_to_current_workspace(i.data(c, QtCore.Qt.UserRole)))
        node_tree.setHeaderHidden(True)
        node_tree_wrapper.layout().addWidget(tree_query_input)
        node_tree_wrapper.layout().addWidget(node_tree)

        return node_tree_wrapper

    def create_main_menu(self) -> QtWidgets.QMenuBar:
        # File
        menu_bar = QtWidgets.QMenuBar()
        file_menu = QtWidgets.QMenu('&File')
        menu_file_load_css = QtWidgets.QAction('Reload css', file_menu)
        menu_file_load_css.setShortcut(QtGui.QKeySequence('Ctrl+R'))
        menu_file_load_css.connect(QtCore.SIGNAL('triggered()'), self.load_style)
        # file_menu.addAction(menu_file_load_css)

        menu_file_new = QtWidgets.QAction('New workflow', file_menu)
        menu_file_new.connect(QtCore.SIGNAL('triggered()'), self.new_file)
        menu_file_new.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.New))
        file_menu.addAction(menu_file_new)
        file_menu.addSeparator()
        menu_file_save = QtWidgets.QAction('Save workflow', file_menu)
        menu_file_save.connect(QtCore.SIGNAL('triggered()'), self.save_file)
        menu_file_save.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Save))
        file_menu.addAction(menu_file_save)
        menu_file_save_as = QtWidgets.QAction('Save workflow as...', file_menu)
        menu_file_save_as.connect(QtCore.SIGNAL('triggered()'), lambda: self.save_file(True))
        menu_file_save_as.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SaveAs))
        file_menu.addAction(menu_file_save_as)
        menu_file_open = QtWidgets.QAction('Open workflow...', file_menu)
        menu_file_open.connect(QtCore.SIGNAL('triggered()'), self.open_file)
        menu_file_open.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Open))
        file_menu.addAction(menu_file_open)
        file_menu.addSeparator()
        menu_file_quit = QtWidgets.QAction('Quit', file_menu)
        menu_file_quit.connect(QtCore.SIGNAL('triggered()'), self.quit_app)
        menu_file_quit.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Quit))
        file_menu.addAction(menu_file_quit)

        # Edit

        # View
        view_menu = QtWidgets.QMenu('&View')
        action_show_node_list = QtWidgets.QAction('Show node list', view_menu)
        action_show_node_list.setCheckable(True)
        action_show_node_list.setChecked(True)
        action_show_node_list.connect(QtCore.SIGNAL('triggered()'),
                                      lambda: self.node_list.setVisible(not self.node_list.isVisible()))

        action_show_node_results = QtWidgets.QAction('Show node results', view_menu)
        action_show_node_results.setCheckable(True)
        action_show_node_results.setChecked(True)
        action_show_node_results.setChecked(self.data_list.isVisible())
        action_show_node_results.connect(QtCore.SIGNAL('triggered()'),
                                         lambda: self.data_list.setVisible(not self.data_list.isVisible()))

        view_menu.addAction(action_show_node_list)
        view_menu.addAction(action_show_node_results)

        # Workflow
        wf_menu = QtWidgets.QMenu('&Workflow')
        self.action_run = QtWidgets.QAction('Run')
        self.action_run.setShortcut(QtGui.QKeySequence('Ctrl+r'))
        self.action_run.setIcon(QtGui.QIcon(assets.get_asset('icons8-play-50.png')))
        self.action_run.connect(QtCore.SIGNAL('triggered()'), self.run_active_workflow)
        wf_menu.addAction(self.action_run)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(wf_menu)

        return menu_bar

    def quit_app(self):
        logging.getLogger('creator').debug('Exiting creator')
        sys.exit(0)

    def new_file(self):
        self.create_workflow_tab('New file')

    def open_file(self):
        dlg = QtWidgets.QFileDialog()
        filename = dlg.getOpenFileName(self, 'Open workflow file', filter='Way files (*.way);;All files (*.*)')[0]

        if filename == '':
            return

        nodes = wayfiles.load(filename)

        widget = self.create_workflow_tab()
        self.tab_bar.setCurrentWidget(widget)
        assert isinstance(widget, AxWorkflowWidget)
        container = widget.widget()
        assert isinstance(container, AxNodeWidgetContainer)

        container.clear()
        for node in nodes:
            node.setParent(container)
            node.show()
            container.discover_nodes()

        widget.set_filename(filename)
        widget.set_modified(False)

    def save_file(self, save_as=False):
        widget = self.tab_bar.currentWidget()
        assert isinstance(widget, AxWorkflowWidget)
        container = widget.widget()
        assert isinstance(container, AxNodeWidgetContainer)

        dlg = QtWidgets.QFileDialog()

        if widget.filename == '' or save_as:
            filename = dlg.getSaveFileName(self, 'Save workflow', filter='Way files (*.way);;All files (*.*)')[0]

            if filename == '':
                return

            widget.set_filename(filename)

        wayfiles.dump(widget.filename, container.get_nodes())
        widget.set_modified(False)

    def tab_closed(self, index):
        widget = self.tab_bar.widget(index)
        assert isinstance(widget, AxWorkflowWidget)

        if widget.modified:
            ans = QtWidgets.QMessageBox.question(self, 'Close tab', 'There are unsaved changes in this workflow.\n' + \
                                                 'Do you want to save your changes?', QtWidgets.QMessageBox.Yes,
                                                 QtWidgets.QMessageBox.No)

            if ans == QtWidgets.QMessageBox.Yes:
                self.save_file()
                return

        self.tab_bar.removeTab(index)

    def load_style(self):
        with open(assets.get_asset('style.css'), 'r') as f:
            logging.getLogger('creator').debug('Applying stylesheet...')
            self.setStyleSheet(f.read())

    def run_active_workflow(self):
        try:
            node_container = self.tab_bar.currentWidget().widget()
        except AttributeError:
            logging.getLogger('creator').info('Run Workflow: No workflows currently open.')
            return

        assert isinstance(node_container, AxNodeWidgetContainer)

        selected_node = node_container.get_selected_node()
        if selected_node is not None:
            root_node = node_container.get_root_node(selected_node)
            ax_nodes = node_container.extract_node_hierarchy_from_widgets(root_node)

            run_task = tasks.RunWorkflowTask(ax_nodes)
            run_task.set_on_finish(self.run_finished)
            run_task.get_workflow().add_listener(Workflow.EVENT_NODE_RUN_FINISHED, self.node_run_finished)

            self.data_list.clear()
            self.action_run.setEnabled(False)

            logging.getLogger('creator').debug('Starting workflow thread...')
            run_task.start()
        else:
            logging.getLogger('creator').debug('No node selection found. Stopping run.')

    def node_run_finished(self, data):
        logging.getLogger('creator').debug('Collecting inputs and outputs from node...')

        node = data['node']
        assert isinstance(node, Node)

        node_item = QtWidgets.QTreeWidgetItem()
        node_item.setText(0, get_node_info(node)['name'])
        inputs = QtWidgets.QTreeWidgetItem()

        # Update data tree with current node
        if not node.has_input() or node.get_input().size() == 0:
            inputs.setText(0, 'Inputs: None')
        else:
            inputs.setText(0, 'Inputs')

            for inp in node.get_input().items():
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, inp.__class__.__name__ + ': ' + str(inp))

                inputs.addChild(item)

        outputs = QtWidgets.QTreeWidgetItem()

        if node.get_output() is None or node.get_output().size() == 0:
            outputs.setText(0, 'Output: None')
        else:
            outputs.setText(0, 'Output')

            for outp in node.get_output().items():
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, outp.__class__.__name__ + ': ' + str(outp))
                outputs.addChild(item)

        node_item.addChild(inputs)
        inputs.setExpanded(True)
        node_item.addChild(outputs)
        outputs.setExpanded(True)

        self.data_tree.insertTopLevelItem(self.data_tree.topLevelItemCount(), node_item)
        node_item.setExpanded(True)

    def run_finished(self, task: tasks.RunWorkflowTask):
        logging.getLogger('creator').debug('Workflow task has finished')
        self.action_run.setEnabled(True)

    def add_node_to_current_workspace(self, node):
        if self.tab_bar.currentWidget() == None:
            widget = self.create_workflow_tab()
            widget.set_modified(True)
            wrapper = widget.widget()
        else:
            wrapper = self.tab_bar.currentWidget().widget()

        ui_node = AxNodeWidget(node(), wrapper)
        ui_node.move(10, 10)
        ui_node.show()

        wrapper.discover_nodes()

    def load_node_tree(self):

        def iter_nodes(parent_item, nodes):
            for node in nodes:
                if get_node_info(node)['hide']:
                    continue

                node_item = QtWidgets.QTreeWidgetItem()
                node_item.setText(0, get_node_info(node)['name'])
                node_item.setData(0, QtCore.Qt.UserRole, node)
                node_item.setIcon(0, QtGui.QIcon(assets.get_asset('icons8-box-50.png')))
                parent_item.addChild(node_item)

            return parent_item

        self.node_list.clear()

        for group, nodes in self.workflow_ctx.get_nodes().items():
            group_item = QtWidgets.QTreeWidgetItem()
            group_item.setText(0, group)

            if isinstance(nodes, dict):
                for subgroup, nodes_2 in nodes.items():
                    subgroup_item = QtWidgets.QTreeWidgetItem()
                    subgroup_item.setText(0, subgroup)
                    subgroup_item = iter_nodes(subgroup_item, nodes_2)
                    group_item.addChild(subgroup_item)

            elif isinstance(nodes, list):
                group_item = iter_nodes(group_item, nodes)

            self.node_list.get_tree().insertTopLevelItem(0, group_item)
            self.node_list.get_tree().expandAll()

    def create_workflow_tab(self, title: str = 'New workflow') -> AxWorkflowWidget:
        scroll_area = AxWorkflowWidget()
        wrapper = AxNodeWidgetContainer(scroll_area)
        scroll_area.setWidget(wrapper)
        wrapper.resize(scroll_area.width(), scroll_area.height())

        self.tab_bar.addTab(scroll_area, title)
        return scroll_area
