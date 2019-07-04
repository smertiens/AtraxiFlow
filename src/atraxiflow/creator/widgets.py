#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from PySide2 import QtCore, QtWidgets, QtGui
from atraxiflow.core import Node, get_node_info
from atraxiflow.base import assets
from atraxiflow.exceptions import *


class AxFileLineEditWidget(QtWidgets.QWidget):
    text_changed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filter = 'All files (*.*)'

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: self.text_changed.emit(s))
        self.btn = QtWidgets.QPushButton('...')
        self.btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.btn.connect(QtCore.SIGNAL('clicked()'), self.show_file_dialog)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.line_edit)
        self.layout().addWidget(self.btn)

    def show_file_dialog(self):
        dlg = QtWidgets.QFileDialog()
        path = dlg.getOpenFileName(self, 'Find file', filter=self.filter)
        path = path[0]

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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(0)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.setIconSize(QtCore.QSize(20, 20))

        self.action_remove = QtWidgets.QAction('-', self.toolbar)
        self.action_remove.connect(QtCore.SIGNAL('triggered()'), self.remove_selected)
        self.action_remove.setIcon(QtGui.QIcon(assets.get_asset('icons8-remove-50.png')))

        self.toolbar.addAction(self.action_remove)

        self.layout().addWidget(self.list_widget)
        self.layout().addWidget(self.toolbar)

    def add_toolbar_action(self, action):
        self.toolbar.insertAction(self.action_remove, action)


class AxNodeWidget(QtWidgets.QFrame):

    def __init__(self, node: Node, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.node = node
        self.selected = False

        self.dock_parent_widget = None
        self.dock_child_widget = None
        self.click_pos = QtCore.QPoint(0, 0)
        self.dock_parent_at_click = None

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setAutoFillBackground(True)

        node_info = get_node_info(node)

        # Title
        node_name = node_info['name'] if node_info['name'] != '' else self.node.__class__.__name__
        self.title_label = QtWidgets.QLabel(node_name)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet(
            'padding: 5px; font-size:12px; font-weight:bold;')
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.btn_close = QtWidgets.QPushButton('x')
        self.btn_close.connect(QtCore.SIGNAL('pressed()'), self.remove)
        self.btn_close.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.btn_close.setFlat(True)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.btn_close)
        # self.title_label.setCursor(QtCore.Qt.SizeAllCursor)

        # Content wrapper
        self.content_wrapper = QtWidgets.QWidget(self)
        self.content_wrapper.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add to window
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addLayout(title_layout)
        # self.layout().addWidget(self.content_wrapper)

        self.build_node_ui()

        self.setMinimumWidth(300)
        self.setMaximumWidth(300)

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
            control = self.node.get_field_ui(name)

            if control is None:
                if prop.get_expected_type()[0] == str:
                    if 'role' in prop.get_display_options():
                        role = prop.get_display_options()['role']

                        if role == 'file':
                            control = AxFileLineEditWidget()
                            control.text_changed.connect(lambda s, prop=prop: prop.set_value(s))
                        elif role == 'select':
                            # TODO: hookup to callback
                            items = prop.get_display_options()['items'] if 'items' in prop.get_display_options() else []
                            control = QtWidgets.QComboBox()
                            control.setEditable(False)
                            control.addItems(items)
                            # control.text_changed.connect(lambda s, prop=prop: prop.set_value(s))
                        else:
                            raise NodeUIException('Role "%s" not found' % role)
                    else:
                        control = QtWidgets.QLineEdit()
                        control.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s, prop=prop: prop.set_value(s))

                elif prop.get_expected_type()[0] == bool:
                    control = QtWidgets.QCheckBox()
                    control.connect(QtCore.SIGNAL('stateChanged(int)'), lambda i, prop=prop: prop.set_value(i == 2))

                elif prop.get_expected_type()[0] == list:
                    raise NodeUIException(
                        'Properties of type dict need to define a custom ui (for example using AxListWidget).')

                elif prop.get_expected_type()[0] == dict:
                    raise NodeUIException('Properties of type dict need to define a custom ui.')

                else:
                    raise NodeUIException('Unrecognized type: %s' % prop.get_expected_type()[0])

            widget.layout().addRow(label, control)

        return widget

    def build_node_ui(self):
        widget = self.node.get_ui()

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
        self.setStyleSheet('background:white')

    def deselect(self):
        self.selected = False
        self.setStyleSheet('')

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.move(self.mapToParent(event.pos() - self.click_pos))

        parent = self
        subnode = self.dock_child_widget
        offset_y = self.y() + self.height()
        while subnode is not None:
            subnode.move(self.x(), offset_y)
            offset_y += subnode.height()
            subnode = subnode.dock_child_widget

        br = QtCore.QPoint(self.x() + self.width(), offset_y)
        parent_w = br.x() + 10 if br.x() > self.parent().width() + 10 else self.parent().width()
        parent_h = br.y() + 10 if br.y() > self.parent().height() + 10 else self.parent().height()
        self.parent().resize(parent_w, parent_h)

        self.parent().dock_neighbours(self)


class AxNodeWidgetContainer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []

    def get_root_node(self, node_widget: AxNodeWidget) -> AxNodeWidget:
        while node_widget.dock_parent_widget is not None:
            node_widget = node_widget.dock_parent_widget

        return node_widget

    def remove_node(self, node: AxNodeWidget):

        if node.dock_parent_widget is not None:
            node.dock_parent_widget.dock_child_widget = None

        if node.dock_child_widget is not None:
            node.dock_child_widget.dock_parent_widget = None

        self.nodes.remove(node)
        node.deleteLater()

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

        for child in self.children():
            if isinstance(child, AxNodeWidget):
                self.nodes.append(child)

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
        radius = 10

        for node in self.nodes:
            if node == widget:
                continue

            hot_area = QtCore.QRect(
                node.pos() + node.rect().bottomLeft() - QtCore.QPoint(radius, radius),
                QtCore.QSize(node.rect().width() + 2 * radius, 4 * radius)
            )

            if hot_area.contains(widget.pos()) or hot_area.contains(widget.rect().topRight()) and (
                    node.dock_child_widget is None):
                self.dock(node, widget)
            else:
                if node == widget.dock_parent_widget:
                    self.undock(node, widget)
