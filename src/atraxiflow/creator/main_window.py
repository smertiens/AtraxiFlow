#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import sys

from atraxiflow import util
from atraxiflow.base.filesystem import *
from atraxiflow.core import Node
from atraxiflow.creator import assets, tasks
from atraxiflow.creator.about_dialog import *
from atraxiflow.creator.nodes import WorkflowNode
from atraxiflow.creator.wayfiles import *
from atraxiflow.creator.widgets import *
from atraxiflow.preferences import PreferencesProvider

__all__ = ['CreatorMainWindow']


class CreatorMainWindow(QtWidgets.QMainWindow):

    WND_SETTINGS_VERSION = 100

    def __init__(self):
        super().__init__()

        self.pref = PreferencesProvider()
        self.n_new_workspace = 1

        # Context needed for pulling available nodes
        self.workflow_ctx = WorkflowContext()
        logging.getLogger('creator').debug('Building main window...')

        # Tab bar - displays the currently opened workflows
        self.tab_bar = QtWidgets.QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.connect(QtCore.SIGNAL('tabCloseRequested(int)'), self.tab_closed)
        self.tab_bar.setStyleSheet('QTabBar::close-button {image: url(%s); }' % assets.get_asset('icons8-delete-16.png'))

        # Splitter between node list and workflow area
        horiz_splitter = QtWidgets.QSplitter()
        self.node_list = AxNodeTreeWidget()  # self.create_node_list_widget()
        self.node_list.node_dbl_clicked.connect(self.node_tree_item_dblclick)
        horiz_splitter.addWidget(self.node_list)
        horiz_splitter.addWidget(self.tab_bar)
        horiz_splitter.setStretchFactor(0, 2)
        horiz_splitter.setStretchFactor(1, 3)

        # Splitter between node list/workflow area and data tree
        vertical_splitter = QtWidgets.QSplitter()
        vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        vertical_splitter.addWidget(horiz_splitter)
        self.data_list = self.create_data_tree_widget()
        vertical_splitter.addWidget(self.data_list)
        vertical_splitter.setStretchFactor(0, 3)
        vertical_splitter.setStretchFactor(1, 1)

        # Central widget - holds node tree, data tree and workflow area
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout())
        central_widget.layout().setSpacing(0)
        central_widget.layout().setContentsMargins(0, 0, 0, 0)
        central_widget.layout().addWidget(vertical_splitter)

        # Add components to main window
        self.setMenuBar(self.create_main_menu())
        self.load_recent_files_list()
        self.setCentralWidget(central_widget)

        # Setup window title, style and size/position
        self.setWindowTitle('AtraxiFlow - Creator')
        self.load_style()
        self.resize(1024, 800)

        # Create default tab with new, empty workflow
        self.create_workflow_tab()

        # Load available nodes to tree
        logging.getLogger('creator').debug('Loading nodes...')
        self.load_node_tree()

        self.restore_window_settings()

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
                          lambda i, c: self.node_tree_item_dblclick(i.data(c, QtCore.Qt.UserRole)))
        node_tree.setHeaderHidden(True)
        node_tree_wrapper.layout().addWidget(tree_query_input)
        node_tree_wrapper.layout().addWidget(node_tree)

        return node_tree_wrapper

    def create_main_menu(self) -> QtWidgets.QMenuBar:
        # File
        menu_bar = QtWidgets.QMenuBar()
        self.file_menu = QtWidgets.QMenu('&File')

        menu_file_new = QtWidgets.QAction('New workspace', self.file_menu)
        menu_file_new.connect(QtCore.SIGNAL('triggered()'), self.new_file)
        menu_file_new.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.New))
        self.file_menu.addAction(menu_file_new)
        self.file_menu.addSeparator()
        menu_file_save = QtWidgets.QAction('Save workspace', self.file_menu)
        menu_file_save.connect(QtCore.SIGNAL('triggered()'), self.save_file)
        menu_file_save.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Save))
        self.file_menu.addAction(menu_file_save)
        menu_file_save_as = QtWidgets.QAction('Save workspace as...', self.file_menu)
        menu_file_save_as.connect(QtCore.SIGNAL('triggered()'), lambda: self.save_file(True))
        menu_file_save_as.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SaveAs))
        self.file_menu.addAction(menu_file_save_as)
        menu_file_open = QtWidgets.QAction('Open workspace...', self.file_menu)
        menu_file_open.connect(QtCore.SIGNAL('triggered()'), self.open_file)
        menu_file_open.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Open))
        self.file_menu.addAction(menu_file_open)

        self.menu_file_recent = self.file_menu.addMenu('Reopen file')

        self.file_menu.addSeparator()
        menu_file_quit = QtWidgets.QAction('Quit', self.file_menu)
        menu_file_quit.connect(QtCore.SIGNAL('triggered()'), self.quit_app)
        menu_file_quit.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Quit))
        self.file_menu.addAction(menu_file_quit)

        # Edit
        # delete node

        # View
        view_menu = QtWidgets.QMenu('&View')
        action_show_node_list = QtWidgets.QAction('Show node list', view_menu)
        action_show_node_list.setCheckable(True)
        action_show_node_list.setChecked(self.pref.get('ui_show_node_list', True))
        self.node_list.setVisible(self.pref.get('ui_show_node_list', True))
        action_show_node_list.connect(QtCore.SIGNAL('triggered()'), self.toggle_node_list)

        action_show_node_results = QtWidgets.QAction('Show node results', view_menu)
        action_show_node_results.setCheckable(True)
        action_show_node_results.setChecked(self.pref.get('ui_show_node_results', True))
        self.data_list.setVisible(self.pref.get('ui_show_node_results', True))
        action_show_node_results.connect(QtCore.SIGNAL('triggered()'), self.toggle_node_results)

        view_menu.addAction(action_show_node_list)
        view_menu.addAction(action_show_node_results)

        # Workflow
        help_menu = QtWidgets.QMenu('&Help')
        self.action_about = QtWidgets.QAction('About...', help_menu)
        self.action_about.connect(QtCore.SIGNAL('triggered()'), self.show_about_dlg)
        help_menu.addAction(self.action_about)

        menu_bar.addMenu(self.file_menu)
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(help_menu)

        if util.is_debug():
            dev_menu = QtWidgets.QMenu('&Developer')
            menu_file_load_css = QtWidgets.QAction('Reload css', dev_menu)
            menu_file_load_css.setShortcut(QtGui.QKeySequence('Ctrl+R'))
            menu_file_load_css.connect(QtCore.SIGNAL('triggered()'), self.load_style)
            dev_menu.addAction(menu_file_load_css)

            menu_bar.addMenu(dev_menu)

        return menu_bar

    def toggle_node_list(self):
        self.node_list.setVisible(not self.node_list.isVisible())
        self.pref.set('ui_show_node_list', self.node_list.isVisible())
        self.pref.save()

    def toggle_node_results(self):
        self.data_list.setVisible(not self.data_list.isVisible())
        self.pref.set('ui_show_node_results', self.data_list.isVisible())
        self.pref.save()

    def show_about_dlg(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def load_recent_files_list(self):
        self.recent_files_list = self.pref.get('creator_recent_files', [])

        # File - Recent files
        self.menu_file_recent.clear()
        for recent_file_entry in self.recent_files_list:
            action_recent = QtWidgets.QAction(recent_file_entry, self.menu_file_recent)
            action_recent.connect(QtCore.SIGNAL('triggered()'), lambda recent_file_entry=recent_file_entry:
            self.open_file(recent_file_entry))
            self.menu_file_recent.addAction(action_recent)

    def add_recent_file_entry(self, entry):
        list_max_size = 5

        if len(self.recent_files_list) == list_max_size:
            self.recent_files_list.pop()

        if entry in self.recent_files_list:
            self.recent_files_list.remove(entry)

        self.recent_files_list.insert(0, entry)
        self.pref.set('creator_recent_files', self.recent_files_list)
        self.pref.save()

        self.load_recent_files_list()

    def quit_app(self):
        logging.getLogger('creator').debug('Exiting creator')
        sys.exit(0)

    def new_file(self):
        self.create_workflow_tab()

    def open_file(self, filename=None):
        if filename is None:
            dlg = QtWidgets.QFileDialog()
            filename = dlg.getOpenFileName(self, 'Open workspace file', filter='Way files (*.way);;All files (*.*)')[0]

            if filename == '':
                return

        wayfile = Wayfile()
        wayfile.load(filename)

        widget = self.create_workflow_tab()
        self.tab_bar.setCurrentWidget(widget)
        assert isinstance(widget, AxWorkflowWidget)
        container = widget.widget()
        assert isinstance(container, AxNodeWidgetContainer)

        container.clear()

        map_node_ids_to_instance = {}
        loaded_nodes = []

        for wf in wayfile.workflows:

            if not isinstance(wf, WayDefaultWorkflow):
                # create workflow node
                wf_ax_node = WorkflowNode({
                    'name': wf.name
                })
                wf_widget = AxWorkflowNodeWidget(wf_ax_node, container)
                wf_widget.run_triggered.connect(lambda: self.run_workflow_node(wf_widget))

                if 'creator_pos' in wf.data:
                    wf_widget.move(wf.data['creator_pos'][0], wf.data['creator_pos'][1])
                else:
                    logging.getLogger('creator').warning('No widget positions for Workflow widget found in wayfile')

                wf_widget.show()

            for n, wf_node in enumerate(wf.get_nodes()):
                node_widget = AxNodeWidget(wf_node.node, container)

                if not isinstance(wf, WayDefaultWorkflow) and n == 0:
                    # first node of workflow needs to be connected to the workflow node
                    container.dock(wf_widget, node_widget)

                if 'creator_pos' in wf_node.data:
                    node_widget.move(wf_node.data['creator_pos'][0], wf_node.data['creator_pos'][1])
                else:
                    logging.getLogger('creator').warning('No widget positions for node widget found in wayfile')

                # assign temp values for parent/children
                if 'creator_child' in wf_node.data:
                    setattr(node_widget, '_tmp_child', wf_node.data['creator_child'])
                if 'creator_parent' in wf_node.data:
                    setattr(node_widget, '_tmp_parent', wf_node.data['creator_parent'])

                if 'creator_id' in wf_node.data:
                    map_node_ids_to_instance[wf_node.data['creator_id']] = node_widget
                else:
                    logging.getLogger('creator').warning('No creator:id property found for node.')

                node_widget.get_node().load_ui_data()
                node_widget.show()
                loaded_nodes.append(node_widget)

        # Dock widgets
        # This will replace node id's with the actual node widget instance
        for node_widget in loaded_nodes:
            if node_widget._tmp_child is not None:
                node_widget.dock_child_widget = map_node_ids_to_instance[node_widget._tmp_child]
            delattr(node_widget, '_tmp_child')

            if node_widget._tmp_parent is not None:
                node_widget.dock_parent_widget = map_node_ids_to_instance[node_widget._tmp_parent]
            delattr(node_widget, '_tmp_parent')

        # register nodes
        container.discover_nodes()

        widget.set_filename(filename)
        widget.set_modified(False)
        self.add_recent_file_entry(filename)

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

        way = Wayfile()
        processed_nodes = []
        workflow_nodes = []

        # collect workflow nodes
        for ui_node in container.get_nodes():
            assert isinstance(ui_node, AxNodeWidget)
            ax_node = ui_node.get_node()
            ax_node.apply_ui_data()

            if isinstance(ax_node, WorkflowNode):
                workflow_nodes.append(ui_node)

        # create workflows and add the workflow nodes children to them
        for wf_ui_node in workflow_nodes:
            wf = WayWorkflow(wf_ui_node.get_node().property('name').value(), {
                'creator_pos': (wf_ui_node.pos().x(), wf_ui_node.pos().y())
            })
            workflow_child_nodes = container.extract_widget_hierarchy_from_root_widget(wf_ui_node)
            workflow_child_nodes.pop(0)  # remove first element since it's the workflow node itself

            for workflow_child_node in workflow_child_nodes:
                assert isinstance(workflow_child_node, AxNodeWidget)

                creator_data = {
                    'creator_id': workflow_child_node.id,
                    'creator_pos': (workflow_child_node.pos().x(), workflow_child_node.pos().y())
                }

                if workflow_child_node.dock_parent_widget is not None and not \
                        isinstance(workflow_child_node.dock_parent_widget.get_node(), WorkflowNode):
                    creator_data['creator_parent'] = workflow_child_node.dock_parent_widget.id

                if workflow_child_node.dock_child_widget is not None:
                    creator_data['creator_child'] = workflow_child_node.dock_child_widget.id

                wf_node = WayNode(workflow_child_node.get_node(), creator_data)
                wf.add_node(wf_node)
                processed_nodes.append(workflow_child_node.id)

            way.add_workflow(wf)
            processed_nodes.append(wf_ui_node.id)

        # collect all other nodes that are not bound to a workflow and add them to the default workflow
        def_wf = WayDefaultWorkflow('')
        for ui_node in container.get_nodes():
            assert isinstance(ui_node, AxNodeWidget)

            if ui_node.id in processed_nodes:
                # skip the node since it was already added as part of a workflow before
                continue

            creator_data = {
                'creator_id': ui_node.id,
                'creator_pos': (ui_node.pos().x(), ui_node.pos().y())
            }

            if ui_node.dock_parent_widget is not None:
                creator_data['creator_parent'] = ui_node.dock_parent_widget.id

            if ui_node.dock_child_widget is not None:
                creator_data['creator_child'] = ui_node.dock_child_widget.id

            def_wf.add_node(WayNode(ui_node.get_node(), creator_data))

        way.add_workflow(def_wf)

        way.save(widget.filename)
        widget.set_modified(False)

    def tab_closed(self, index):
        widget = self.tab_bar.widget(index)
        assert isinstance(widget, AxWorkflowWidget)

        if widget.modified:
            ans = QtWidgets.QMessageBox.question(self, 'Close tab', 'There are unsaved changes in this workspace.\n' + \
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

    def run_workflow_node(self, wf_node: AxWorkflowNodeWidget):
        node_container = wf_node.parent()
        assert isinstance(node_container, AxNodeWidgetContainer)

        ax_nodes = node_container.extract_node_hierarchy_from_widgets(wf_node)

        self.data_list.clear()

        wf_item = QtWidgets.QTreeWidgetItem()
        if isinstance(wf_node.get_node(), WorkflowNode):
            wf_item.setText(0, 'Workflow: %s' % wf_node.get_node().property('name').value())
            ax_nodes.pop(0)  # Workflow nodes should not be processed
        else:
            wf_item.setText(0, 'Workflow: (default)')
        self.data_list.insertTopLevelItem(0, wf_item)
        wf_item.setExpanded(True)

        run_task = tasks.RunWorkflowTask(ax_nodes)
        run_task.set_on_finish(self.run_finished)
        run_task.get_workflow().add_listener(Workflow.EVENT_NODE_RUN_FINISHED, self.node_run_finished)

        self.action_run.setEnabled(False)

        logging.getLogger('creator').debug('Starting workflow thread...')
        run_task.start()

    def run_active_workflow(self):
        try:
            node_container = self.tab_bar.currentWidget().widget()
        except AttributeError:
            logging.getLogger('creator').info('Run Workflow: No workspaces currently open.')
            return

        assert isinstance(node_container, AxNodeWidgetContainer)

        selected_node = node_container.get_selected_node()
        if selected_node is not None:
            root_node = node_container.get_root_node(selected_node)

            if not isinstance(root_node, AxWorkflowNodeWidget):
                logging.getLogger('creator').error('You need to parent your nodes to a workflow to run them.')
                return

            self.run_workflow_node(root_node)

        else:
            logging.getLogger('creator').debug('No node selection found. Stopping run.')

    def node_run_finished(self, data):
        logging.getLogger('creator').debug('Collecting inputs and outputs from node...')

        node = data['node']
        assert isinstance(node, Node)

        node_item = QtWidgets.QTreeWidgetItem()
        node_item.setText(0, get_node_info(node)['name'])
        node_item.setIcon(0, QtGui.QIcon(assets.get_asset('icons8-cube-50.png')))
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

        root = self.data_list.topLevelItem(0)
        root.addChild(node_item)
        node_item.setExpanded(True)

    def run_finished(self, task: tasks.RunWorkflowTask):
        logging.getLogger('creator').debug('Workflow task has finished')
        self.action_run.setEnabled(True)

    def node_tree_item_dblclick(self, node):

        if self.tab_bar.currentWidget() == None:
            widget = self.create_workflow_tab()
            widget.set_modified(True)
            wrapper = widget.widget()
        else:
            wrapper = self.tab_bar.currentWidget().widget()

        node = node()

        if isinstance(node, WorkflowNode):
            ui_node = AxWorkflowNodeWidget(node, wrapper)
            ui_node.run_triggered.connect(lambda: self.run_workflow_node(ui_node))
        else:
            ui_node = AxNodeWidget(node, wrapper)

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
                node_item.setIcon(0, QtGui.QIcon(assets.get_asset('icons8-cube-50.png')))
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

        # add Workflow item at the top
        workflow_item = QtWidgets.QTreeWidgetItem()
        workflow_item.setText(0, 'Workflow')
        workflow_item.setData(0, QtCore.Qt.UserRole, WorkflowNode)
        workflow_item.setIcon(0, QtGui.QIcon(assets.get_asset('icons8-module-50.png')))
        self.node_list.get_tree().insertTopLevelItem(0, workflow_item)

    def create_workflow_tab(self, title: str = None) -> AxWorkflowWidget:
        if title is None:
            title = 'New Workspace %s' % self.n_new_workspace
            self.n_new_workspace += 1

        scroll_area = AxWorkflowWidget()
        wrapper = AxNodeWidgetContainer(scroll_area)
        scroll_area.setWidget(wrapper)
        wrapper.resize(scroll_area.width(), scroll_area.height())

        self.tab_bar.addTab(scroll_area, title)
        return scroll_area

    def closeEvent(self, event: QtGui.QCloseEvent):
        logging.getLogger('creator').debug('Closing main window..')
        for n in range(0, self.tab_bar.count() - 1):
            self.tab_closed(n)

        logging.getLogger('creator').debug('Saving settings...')
        with open(self.pref.get_settings_file('mainwindow.geo'), 'wb') as f:
            f.write(self.saveGeometry().data())

    def restore_window_settings(self):
        if os.path.exists(self.pref.get_settings_file('mainwindow.geo')):
            logging.getLogger('creator').debug('Restoring geometry...')

            with open(self.pref.get_settings_file('mainwindow.geo'), 'rb') as f:
                self.restoreGeometry(f.read())
