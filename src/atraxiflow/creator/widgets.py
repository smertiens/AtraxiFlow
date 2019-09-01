#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging
import os
import re
import uuid

from PySide2 import QtCore, QtWidgets, QtGui

from atraxiflow.core import Node, get_node_info
from atraxiflow.creator import assets
from atraxiflow.exceptions import *

__all__ = ['AxNodeTreeWidget', 'AxNodeWidget', 'AxWorkflowWidget', 'AxNodeWidgetContainer', 'AxListWidget',
           'AxFileLineEditWidget', 'AxWorkflowNodeWidget']


class AxFileLineEditWidget(QtWidgets.QWidget):
    text_changed = QtCore.Signal(str)
    FindFile = 'FindFile'
    FindFolder = 'FindFolder'
    SaveFile = 'SaveFile'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.find = self.FindFile
        self.filter = 'All files (*.*)'

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.text_changed.emit(s))
        self.line_edit.setObjectName('ax_filelineedit_input')
        self.btn = QtWidgets.QPushButton()
        self.btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.btn.connect(QtCore.SIGNAL('clicked()'), self.show_file_dialog)
        self.btn.setObjectName('ax_filelineedit_button')
        self.btn.setIcon(QtGui.QIcon(assets.get_asset('icons8-opened-folder-50.png')))
        self.btn.setFlat(True)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.line_edit)
        self.layout().addWidget(self.btn)

    def set_find_mode(self, mode):
        self.find = mode

    def show_file_dialog(self):
        dlg = QtWidgets.QFileDialog()
        path = ''

        if self.find == self.FindFile:
            path = dlg.getOpenFileName(self, 'Find file', filter=self.filter)
            path = path[0]

        elif self.find == self.SaveFile:
            path = dlg.getSaveFileName(self, 'Save file', filter=self.filter)
            path = path[0]

        elif self.find == self.FindFolder:
            path = dlg.getExistingDirectory(self, 'Find folder', options=QtWidgets.QFileDialog.ShowDirsOnly)

        if path != '':
            self.line_edit.setText(path)


class AxListWidget(QtWidgets.QWidget):
    list_changed = QtCore.Signal()

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_toolbar(self):
        return self.toolbar

    def get_list(self) -> QtWidgets.QListWidget:
        return self.list_widget

    def get_item_list(self) -> list:
        result = []
        for n in range(0, self.list_widget.count()):
            result.append(self.list_widget.item(n).text())
        return result

    def add_items(self, items):
        self.list_widget.addItems(items)
        self.list_changed.emit()

    def add_item(self, item):
        self.list_widget.addItem(item)
        self.list_changed.emit()

    def __init__(self, parent=None, show_edit_button=True):
        super().__init__(parent)

        self.show_edit_button = show_edit_button

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(0)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setFixedHeight(140)
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.setIconSize(QtCore.QSize(20, 20))

        self.action_remove = QtWidgets.QAction('Remove item', self.toolbar)
        self.action_remove.connect(QtCore.SIGNAL('triggered()'), self.remove_selected)
        self.action_remove.setIcon(QtGui.QIcon(assets.get_asset('icons8-remove-50.png')))
        self.toolbar.addAction(self.action_remove)

        if self.show_edit_button:
            self.action_edit = QtWidgets.QAction('Edit item', self.toolbar)
            self.action_edit.connect(QtCore.SIGNAL('triggered()'), self.edit_selected)
            self.action_edit.setIcon(QtGui.QIcon(assets.get_asset('icons8-edit-50.png')))
            self.toolbar.addAction(self.action_edit)

        self.layout().addWidget(self.list_widget)
        self.layout().addWidget(self.toolbar)

    def add_toolbar_action(self, action):
        self.toolbar.insertAction(self.action_remove, action)

    def add_toolbar_widget(self, w):
        self.toolbar.insertWidget(self.action_remove, w)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.list_widget.setEnabled(enabled)
        self.toolbar.setEnabled(enabled)

    def edit_selected(self):
        if len(self.list_widget.selectedItems()) == 0:
            return

        item = self.list_widget.selectedItems()[0]

        dlg_result = QtWidgets.QInputDialog.getText(self, 'Edit list item', 'Enter the new value for the current item:',
                                                    text=item.text())

        if dlg_result[1]:
            item.setText(dlg_result[0])

class AxNodeWidget(QtWidgets.QFrame):

    def __init__(self, node: Node, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.id = str(uuid.uuid4())

        self.node = node
        self.selected = False

        self.dock_parent_widget = None
        self.dock_child_widget = None
        self.click_pos = QtCore.QPoint(0, 0)
        self.dock_parent_at_click = None

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setAutoFillBackground(True)

        node_info = get_node_info(node)

        # Title
        node_name = node_info['name'] if node_info['name'] != '' else self.node.__class__.__name__
        self.title_label = QtWidgets.QLabel(node_name)
        self.title_label.setAlignment(QtCore.Qt.AlignLeft)
        self.title_label.setObjectName('node_title')
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setIcon(QtGui.QIcon(assets.get_asset('icons8-delete-64.png')))
        self.btn_close.setObjectName('node_remove_btn')
        self.btn_close.connect(QtCore.SIGNAL('pressed()'), self.remove)
        self.btn_close.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.btn_close.setFlat(True)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.btn_close)

        # Add to window
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addLayout(title_layout)

        self.build_node_ui()

        win_width = 400
        self.setMinimumWidth(win_width)
        self.setMaximumWidth(win_width)

    def modified(self):
        try:
            wf_widget = self.parent().parent().parent()
            if isinstance(wf_widget, AxWorkflowWidget):
                wf_widget.set_modified(True)
            else:
                raise AttributeError
        except AttributeError:
            logging.getLogger('creator').debug('Could not set modified state, parent is not an AxWorkflowWidget.')

    def get_node(self) -> Node:
        return self.node

    def remove(self):
        self.parent().remove_node(self)

    def get_default_controls(self) -> QtWidgets.QWidget:
        """
        Tries to create a default ui for the given node
        """
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QFormLayout())

        # build default widget
        for name, prop in self.node.get_properties().items():
            label = prop.get_label() if prop.get_label() != '' else name

            # Try to get a widget for the given field from the node
            control = self.node.get_field_ui(name, self)

            if control is None:
                if 'hide_in_ui' in prop.get_display_options() and prop.get_display_options()['hide_in_ui'] == True:
                    continue

                if prop.get_expected_type()[0] == str:
                    if 'role' in prop.get_display_options():
                        role = prop.get_display_options()['role']

                        if role == 'file' or role == 'folder':
                            control = AxFileLineEditWidget()

                            if role == 'folder':
                                control.set_find_mode(control.FindFolder)
                            elif role == 'file' and 'role_file_mode' in prop.get_display_options():
                                if prop.get_display_options()['role_file_mode'] == 'save_file':
                                    control.set_find_mode(control.SaveFile)

                            control.text_changed.connect(lambda s, prop=prop: prop.set_value(s))
                            control.text_changed.connect(self.modified)
                            if isinstance(prop.value(), str):
                                control.line_edit.setText(prop.value())
                        elif role == 'select':
                            items = prop.get_display_options()['items'] if 'items' in prop.get_display_options() else []
                            control = QtWidgets.QComboBox()
                            control.setEditable(False)
                            control.addItems(items)
                            if isinstance(prop.value(), str):
                                control.setCurrentText(prop.value())
                            control.connect(QtCore.SIGNAL('currentTextChanged(QString)'),
                                            lambda s, prop=prop: prop.set_value(s))
                            control.connect(QtCore.SIGNAL('currentTextChanged(QString)'),
                                            lambda s: self.modified())
                        else:
                            raise NodeUIException('Role "%s" not found' % role)
                    else:
                        control = QtWidgets.QLineEdit()
                        control.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s, prop=prop: prop.set_value(s))
                        control.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.modified())
                        if isinstance(prop.value(), str):
                            control.setText(prop.value())

                elif prop.get_expected_type()[0] == bool:
                    control = QtWidgets.QCheckBox()
                    control.connect(QtCore.SIGNAL('stateChanged(int)'), lambda i, prop=prop: prop.set_value(i == 2))
                    control.connect(QtCore.SIGNAL('stateChanged(int)'), lambda i: self.modified())
                    if isinstance(prop.value(), bool):
                        control.setChecked(prop.value())

                elif prop.get_expected_type()[0] == int:
                    max = prop.get_display_options()['max'] if 'max' in prop.get_display_options() else 999999
                    min = prop.get_display_options()['min'] if 'min' in prop.get_display_options() else 0
                    step = prop.get_display_options()['step'] if 'step' in prop.get_display_options() else 1

                    control = QtWidgets.QSpinBox()
                    control.setRange(min, max)
                    control.setSingleStep(step)
                    control.connect(QtCore.SIGNAL('valueChanged(int)'), lambda i, prop=prop: prop.set_value(i))
                    control.connect(QtCore.SIGNAL('valueChanged(int)'), lambda i: self.modified())
                    if isinstance(prop.value(), int):
                        control.setValue(prop.value())

                elif prop.get_expected_type()[0] == float:
                    max = prop.get_display_options()['max'] if 'max' in prop.get_display_options() else 999999.0
                    min = prop.get_display_options()['min'] if 'min' in prop.get_display_options() else 0.0
                    step = prop.get_display_options()['step'] if 'step' in prop.get_display_options() else 1.0
                    decimals = prop.get_display_options()['decimals'] if 'decimals' in prop.get_display_options() else 2

                    control = QtWidgets.QDoubleSpinBox()
                    control.setRange(min, max)
                    control.setSingleStep(step)
                    control.setDecimals(decimals)
                    control.connect(QtCore.SIGNAL('valueChanged(double)'), lambda d, prop=prop: prop.set_value(d))
                    control.connect(QtCore.SIGNAL('valueChanged(double)'), lambda d: self.modified())
                    if isinstance(prop.value(), float):
                        control.setValue(prop.value())

                elif prop.get_expected_type()[0] == list:
                    raise NodeUIException(
                        'Properties of type dict need to define a custom ui (for example using AxListWidget).')

                elif prop.get_expected_type()[0] == dict:
                    raise NodeUIException('Properties of type dict need to define a custom ui.')

                else:
                    raise NodeUIException('Unrecognized type: %s' % prop.get_expected_type()[0])

            label_w = QtWidgets.QLabel(label)
            label_w.setToolTip(prop.get_hint())
            widget.layout().addRow(label_w, control)

        return widget

    def build_node_ui(self):
        widget = self.node.get_ui(self)

        if widget is None:
            widget = self.get_default_controls()

        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout().addWidget(widget)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.click_pos = event.pos()
        self.dock_parent_at_click = self.dock_parent_widget
        self.raise_()
        self.select()

    def select(self):
        self.parent().clear_selection()
        self.selected = True

    def deselect(self):
        self.selected = False
        self.setStyleSheet('')

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.move(self.mapToParent(event.pos() - self.click_pos))

        subnode = self.dock_child_widget
        offset_y = self.y() + self.height()
        while subnode is not None:
            subnode.move(self.x(), offset_y)
            offset_y += subnode.height()
            subnode = subnode.dock_child_widget

        # Resize parent to the new node position
        br = QtCore.QPoint(self.x() + self.width(), offset_y)
        parent_w = br.x() + 10 if br.x() > self.parent().width() + 10 else self.parent().width()
        parent_h = br.y() + 10 if br.y() > self.parent().height() + 10 else self.parent().height()
        self.parent().resize(parent_w, parent_h)

        self.parent().dock_neighbours(self)
        self.modified()


class AxNodeWidgetContainer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.nodes = []

    def get_root_node(self, node_widget: AxNodeWidget) -> AxNodeWidget:
        while node_widget.dock_parent_widget is not None:
            node_widget = node_widget.dock_parent_widget

        return node_widget

    def remove_node(self, node):

        if isinstance(node, AxWorkflowNodeWidget):
            # recursively delete all child nodes
            if node.dock_child_widget is not None:
                if QtWidgets.QMessageBox.question(self, 'Remove workflow',
                                                  'Deleting a workflow will also delete all child nodes. ' +
                                                  'Are you sure you want to continue?',
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                    return

            children = self.extract_widget_hierarchy_from_root_widget(node)
            children.pop(0)  # remove AxWorkflowNodeWidget from list

            for child in children:
                self.remove_node(child)

        if node.dock_parent_widget is not None:
            node.dock_parent_widget.dock_child_widget = None

        if node.dock_child_widget is not None:
            node.dock_child_widget.dock_parent_widget = None

        self.nodes.remove(node)
        node.deleteLater()

    def clear(self):
        for node in self.nodes:
            node.deleteLater()

        self.nodes.clear()

    def extract_widget_hierarchy_from_root_widget(self, root_node: AxNodeWidget) -> list:
        widgets = [root_node]
        while root_node.dock_child_widget is not None:
            widgets.append(root_node.dock_child_widget)
            root_node = root_node.dock_child_widget

        return widgets

    def extract_node_hierarchy_from_widgets(self, root_node: AxNodeWidget) -> list:
        nodes = [root_node.node]
        while root_node.dock_child_widget is not None:
            nodes.append(root_node.dock_child_widget.node)
            root_node = root_node.dock_child_widget

        return nodes

    def get_selected_node(self) -> AxNodeWidget:
        for node in self.nodes:
            if node.selected:
                return node

        return None

    def clear_selection(self):
        for node in self.nodes:
            node.deselect()

    def discover_nodes(self):
        self.nodes.clear()

        w = 0
        h = 0

        for child in self.children():
            if isinstance(child, AxNodeWidget):
                self.nodes.append(child)

                # Resize to fit node position
                w = child.pos().x() + child.rect().width() + 10 if w < child.pos().x() + child.rect().width() + 10 else w
                h = child.pos().y() + child.rect().height() + 10 if h < child.pos().y() + child.rect().height() + 10 else h

        self.resize(w, h)

    def get_nodes(self):
        return self.nodes

    def dock(self, upper: AxNodeWidget, lower: AxNodeWidget, recursive=True):
        lower.move(
            upper.pos().x(),
            upper.pos().y() + upper.rect().height()
        )
        upper.dock_child_widget = lower
        lower.dock_parent_widget = upper

        subnode = lower.dock_child_widget
        if recursive:
            while subnode is not None:
                self.dock(subnode.dock_parent_widget, subnode, False)
                subnode = subnode.dock_child_widget

    def undock(self, upper: AxNodeWidget, lower: AxNodeWidget):
        upper.dock_child_widget = None
        lower.dock_parent_widget = None

    def dock_neighbours(self, widget: AxNodeWidget):
        if isinstance(widget, AxWorkflowNodeWidget):
            return

        radius = 10

        for node in self.nodes:
            if node == widget:
                continue

            hot_area = QtCore.QRect(
                node.pos() + node.rect().bottomLeft() - QtCore.QPoint(radius, radius),
                QtCore.QSize(node.rect().width() + 2 * radius, 4 * radius)
            )

            if hot_area.contains(widget.pos()) or hot_area.contains(widget.rect().topRight()) \
                    and (node.dock_child_widget is None):
                self.dock(node, widget)
            else:
                if node == widget.dock_parent_widget:
                    self.undock(node, widget)


class AxWorkflowNodeWidget(AxNodeWidget):
    run_triggered = QtCore.Signal()

    def __init__(self, node: Node, parent: QtWidgets.QWidget = None):
        super().__init__(node, parent)
        self.setObjectName('ax_workflow_node')

        # Change look of title label
        self.title_label.setObjectName('ax_workflow_node_title')
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setText(node.property('name').value())

        # Create workflow toolbar
        self.action_rename = QtWidgets.QAction('Rename workflow')
        self.action_rename.setIcon(QtGui.QIcon(assets.get_asset('icons8-edit-file-50.png')))
        self.action_rename.connect(QtCore.SIGNAL('triggered()'), self.rename_node)
        self.action_run = QtWidgets.QAction('Run workflow')
        self.action_run.setIcon(QtGui.QIcon(assets.get_asset('icons8-play-50.png')))
        self.action_run.connect(QtCore.SIGNAL('triggered()'), lambda: self.run_triggered.emit())

        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(QtCore.QSize(20, 20))
        toolbar.addAction(self.action_rename)
        toolbar.addAction(self.action_run)

        self.layout().addWidget(toolbar)

    def _validate_workflow_name(self, name) -> bool:
        match = re.match(r'^[\w+ \._\-]+$', name)
        return match is not None

    def rename_node(self):
        new_name, okay = QtWidgets.QInputDialog.getText(self, 'Rename workflow', 'Please enter the new workflow name',
                                                        text=self.node.property('name').value())

        if not okay:
            return

        if not self._validate_workflow_name(new_name):
            QtWidgets.QMessageBox.warning(self, 'Rename workflow', 'Invalid workflow name', QtWidgets.QMessageBox.Ok)
            self.rename_node()
        else:
            self.node.property('name').set_value(new_name)
            self.title_label.setText(new_name)

            workflow_widget = self.parent().parent().parent()
            assert isinstance(workflow_widget, AxWorkflowWidget)
            workflow_widget.set_modified(True)


class AxWorkflowWidget(QtWidgets.QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = ''
        self.unsaved_name = 'New Workspace'
        self.modified = False

    def set_filename(self, filename: str):
        self.filename = filename
        self._update_tab_title()

    def set_modified(self, modified: bool):
        self.modified = modified
        self._update_tab_title()

    def _update_tab_title(self):
        tab_bar = self.parentWidget().parentWidget()
        assert isinstance(tab_bar, QtWidgets.QTabWidget)

        tab_bar.setTabText(tab_bar.currentIndex(),
                           (self.unsaved_name if self.filename == '' else os.path.basename(self.filename)) +
                           (' *' if self.modified else ''))


class AxNodeTreeWidget(QtWidgets.QWidget):
    node_dbl_clicked = QtCore.Signal(Node)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.tree_query_input = QtWidgets.QLineEdit()
        self.tree_query_input.setObjectName('tree_query_input')
        self.tree_query_input.setPlaceholderText('Filter nodes...')
        self.tree_query_input.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.filter_node_tree(s))
        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.setObjectName('node_tree')
        self.node_tree.connect(QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem*, int)'), self.item_dbl_clicked)
        self.node_tree.setHeaderHidden(True)
        self.layout().addWidget(self.tree_query_input)
        self.layout().addWidget(self.node_tree)

    def item_dbl_clicked(self, item: QtWidgets.QTreeWidgetItem, col: int):
        node = item.data(col, QtCore.Qt.UserRole)

        if node is not None:
            self.node_dbl_clicked.emit(node)

    def get_tree(self) -> QtWidgets.QTreeWidget:
        return self.node_tree

    def get_query_input(self) -> QtWidgets.QLineEdit:
        return self.tree_query_input

    def clear(self):
        self.node_tree.clear()

    def filter_node_tree(self, q: str):
        it = QtWidgets.QTreeWidgetItemIterator(self.node_tree)

        while it.value():
            item = it.value()

            if item.childCount() == 0:
                item.setHidden(q.lower() not in item.text(0).lower())

            it += 1
