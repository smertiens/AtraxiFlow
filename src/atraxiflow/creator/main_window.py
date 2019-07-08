#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging, sys, os

from atraxiflow.base.filesystem import *
from atraxiflow.core import Node
from atraxiflow.creator import assets, tasks, wayfiles
from atraxiflow.creator.widgets import AxNodeWidget, AxNodeWidgetContainer


class CreatorMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.workflow_ctx = WorkflowContext()
        self.setWindowTitle('AtraxiFlow - Creator')
        self.load_style()

        logging.getLogger('creator').debug('Building main window...')

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout())
        central_widget.layout().setSpacing(0)
        central_widget.layout().setContentsMargins(0, 0, 0, 0)

        # Tab bar
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)

        ## Main menu
        # File
        menu_bar = QtWidgets.QMenuBar()
        file_menu = QtWidgets.QMenu('&File')
        menu_file_load_css = QtWidgets.QAction('Reload css', file_menu)
        menu_file_load_css.setShortcut(QtGui.QKeySequence('Ctrl+R'))
        menu_file_load_css.connect(QtCore.SIGNAL('triggered()'), self.load_style)
        # file_menu.addAction(menu_file_load_css)

        menu_file_new = QtWidgets.QAction('New workflow', file_menu)
        menu_file_new.connect(QtCore.SIGNAL('triggered()'), self.new_file)
        menu_file_new.setShortcut(QtGui.QKeySequence('Ctrl + N'))
        file_menu.addAction(menu_file_new)
        file_menu.addSeparator()
        menu_file_save = QtWidgets.QAction('Save workflow', file_menu)
        menu_file_save.connect(QtCore.SIGNAL('triggered()'), self.save_file)
        menu_file_save.setShortcut(QtGui.QKeySequence('Ctrl + S'))
        file_menu.addAction(menu_file_save)
        menu_file_save_as = QtWidgets.QAction('Save workflow as...', file_menu)
        menu_file_save_as.connect(QtCore.SIGNAL('triggered()'), lambda: self.save_file(True))
        file_menu.addAction(menu_file_save_as)
        menu_file_open = QtWidgets.QAction('Open workflow file...', file_menu)
        menu_file_open.connect(QtCore.SIGNAL('triggered()'), self.open_file)
        file_menu.addAction(menu_file_open)

        menu_file_quit = QtWidgets.QAction('Quit', file_menu)
        menu_file_quit.connect(QtCore.SIGNAL('triggered()'), self.quit_app)
        file_menu.addAction(menu_file_quit)

        # Workflow
        wf_menu = QtWidgets.QMenu('&Workflow')
        menu_wf_run = QtWidgets.QAction('Run', wf_menu)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(wf_menu)

        # Main toolbar
        main_toolbar = QtWidgets.QToolBar()
        main_toolbar.setMovable(False)

        self.action_play = QtWidgets.QAction('Play', main_toolbar)
        self.action_play.setIcon(QtGui.QIcon(assets.get_asset('icons8-play-50.png')))
        self.action_play.connect(QtCore.SIGNAL('triggered()'), self.run_active_workflow)
        self.action_stop = QtWidgets.QAction('Stop', main_toolbar)
        self.action_stop.setIcon(QtGui.QIcon(assets.get_asset('icons8-stop-50.png')))
        self.action_stop.setEnabled(False)

        # Spacer
        spacer = QtWidgets.QWidget()
        spacer.setObjectName('tb_spacer')
        spacer.resize(10, 10)
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        main_toolbar.addWidget(spacer)
        main_toolbar.addAction(self.action_play)
        main_toolbar.addAction(self.action_stop)

        # Statusbar
        self.status_bar = QtWidgets.QStatusBar()

        # Node list
        node_tree_wrapper = QtWidgets.QWidget()
        node_tree_wrapper.setLayout(QtWidgets.QVBoxLayout())
        node_tree_wrapper.layout().setSpacing(0)
        node_tree_wrapper.layout().setContentsMargins(0, 0, 0, 0)

        tree_query_input = QtWidgets.QLineEdit()
        tree_query_input.setObjectName('tree_query_input')
        tree_query_input.setPlaceholderText('Filter nodes...')
        tree_query_input.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.filter_node_tree(s))
        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.setObjectName('node_tree')
        self.node_tree.connect(QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*, int)'),
                               lambda i, c: self.add_node_to_current_workspace(i.data(c, QtCore.Qt.UserRole)))
        self.node_tree.setHeaderHidden(True)
        node_tree_wrapper.layout().addWidget(tree_query_input)
        node_tree_wrapper.layout().addWidget(self.node_tree)

        # Add data tree
        self.data_tree = QtWidgets.QTreeWidget()
        self.data_tree.setColumnCount(1)
        self.data_tree.setHeaderHidden(True)
        self.data_tree.setObjectName('data_tree')

        horiz_splitter = QtWidgets.QSplitter()
        horiz_splitter.addWidget(node_tree_wrapper)
        horiz_splitter.addWidget(self.tab_bar)

        vertical_splitter = QtWidgets.QSplitter()
        vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        vertical_splitter.addWidget(horiz_splitter)
        vertical_splitter.addWidget(self.data_tree)

        central_widget.layout().addWidget(vertical_splitter)
        self.addToolBar(QtCore.Qt.TopToolBarArea, main_toolbar)
        self.setMenuBar(menu_bar)
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

        # Create default tab
        self.create_workflow_tab('Default Workflow')

        logging.getLogger('creator').debug('Loading nodes...')
        self.load_node_tree()

        self.resize(1024, 800)

    def quit_app(self):
        logging.getLogger('creator').debug('Exiting creator')
        sys.exit(0)

    def new_file(self):
        self.create_workflow_tab('New file')

    def open_file(self):
        dlg = QtWidgets.QFileDialog()
        filename = dlg.getOpenFileName(self, 'Open workflow file', filter='Way files (*.way);;All files (*.*)')

        if filename[0] == '':
            return

        nodes = wayfiles.load(filename[0])

        widget = self.create_workflow_tab(os.path.basename(filename[0]))
        assert isinstance(widget, QtWidgets.QScrollArea)
        container = widget.widget()
        assert isinstance(container, AxNodeWidgetContainer)

        container.clear()
        for node in nodes:
            node.setParent(container)
            node.show()
            container.discover_nodes()

    def save_file(self, save_as=False):
        dlg = QtWidgets.QFileDialog()
        filename = dlg.getSaveFileName(self, 'Save workflow', filter='Way files (*.way);;All files (*.*)')

        if filename[0] == '':
            return

        widget = self.tab_bar.currentWidget()
        assert isinstance(widget, QtWidgets.QScrollArea)
        container = widget.widget()
        assert isinstance(container, AxNodeWidgetContainer)

        wayfiles.dump(filename[0], container.get_nodes())

    def filter_node_tree(self, q: str):
        it = QtWidgets.QTreeWidgetItemIterator(self.node_tree)

        while it.value():
            item = it.value()

            if item.childCount() == 0:
                item.setHidden(q.lower() not in item.text(0).lower())

            it += 1

    def load_style(self):
        with open(assets.get_asset('style.css'), 'r') as f:
            logging.getLogger('creator').debug('Applying stylesheet...')
            self.setStyleSheet(f.read())

    def run_active_workflow(self):
        node_container = self.tab_bar.currentWidget().widget()
        assert isinstance(node_container, AxNodeWidgetContainer)

        selected_node = node_container.get_selected_node()
        if selected_node is not None:
            root_node = node_container.get_root_node(selected_node)
            ax_nodes = node_container.extract_node_hierarchy_from_widgets(root_node)

            run_task = tasks.RunWorkflowTask(ax_nodes, self)
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
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(False)

    def add_node_to_current_workspace(self, node):
        # TODO make clear this will add a node from the node tree
        if node == None:
            # maybe clicked a category
            return

        wrapper = self.tab_bar.currentWidget().widget()
        ui_node = self.create_node_widget(node(), wrapper)
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

        self.node_tree.clear()

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

            self.node_tree.insertTopLevelItem(0, group_item)
            self.node_tree.expandAll()

    def create_node_widget(self, node: Node, parent: AxNodeWidgetContainer):
        return AxNodeWidget(node, parent)

    def create_workflow_tab(self, title: str='New workflow') -> QtWidgets.QScrollArea:
        scroll_area = QtWidgets.QScrollArea()
        wrapper = AxNodeWidgetContainer()
        scroll_area.setWidget(wrapper)
        wrapper.resize(scroll_area.width(), scroll_area.height())

        self.tab_bar.addTab(scroll_area, title)
        return scroll_area
