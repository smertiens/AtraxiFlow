#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from PySide2 import QtCore, QtWidgets, QtGui
from atraxiflow.core import Node

"""
class AxFileSelectionWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.line_edit = QtWidgets.QLineEdit()
        self.btn = QtWidgets.QPushButton('...')
"""

class AxNodeWidget(QtWidgets.QFrame):

    def __init__(self, node: Node, parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        self.node = node

        self.dock_parent_widget = None
        self.dock_child_widget = None
        self.click_pos = QtCore.QPoint(0, 0)
        self.dock_parent_at_click = None

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setAutoFillBackground(True)

        # Title
        self.title_label = QtWidgets.QLabel('Demo')
        # self.title_label.setStyleSheet('border-bottom: 1px solid black')
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.title_label.setCursor(QtCore.Qt.SizeAllCursor)

        # Content wrapper
        self.content_wrapper = QtWidgets.QWidget(self)
        self.content_wrapper.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add to window
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.title_label)
        #self.layout().addWidget(self.content_wrapper)

        self.build_node_ui()

        self.resize(300, 150)

    def get_default_controls(self):
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QFormLayout())


        # build default widget
        for name, prop in self.node.get_properties().items():
            label = prop.get_label() if prop.get_label() != '' else name

            if hasattr(self.node, 'ui_field'):
                control = self.node.ui_field(name)
            else:
                if prop.get_expected_type()[0] == str:
                    control = QtWidgets.QLineEdit()
                elif prop.get_expected_type()[0] == bool:
                    control = QtWidgets.QCheckBox()
                elif prop.get_expected_type()[0] == list:
                    control = QtWidgets.QListWidget()
                else:
                    raise Exception('Unrecognized type: %s' % prop.get_expected_type()[0])

            widget.layout().addRow(label, control)
            return widget

    def build_node_ui(self):
        if hasattr(self.node, 'ui'):
            widget = self.node.ui()
        else:
            widget = self.get_default_controls()

        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout().addWidget(widget)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.click_pos = event.pos()
        self.dock_parent_at_click = self.dock_parent_widget
        self.raise_()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.move(self.mapToParent(event.pos() - self.click_pos))

        parent = self
        subnode = self.dock_child_widget
        while subnode is not None:
            self.parent().dock(parent, subnode)
            parent = subnode
            subnode = subnode.dock_child_widget

        br = self.rect().bottomRight() + self.pos()
        parent_w = br.x() + 10 if br.x() > self.parent().width() + 10 else self.parent().width()
        parent_h = br.x() + 10 if br.y() > self.parent().height() + 10 else self.parent().height()
        self.parent().resize(parent_w, parent_h)

        self.parent().dock_neighbours(self)


class AxNodeWidgetContainer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []

    def discover_nodes(self):
        for child in self.children():
            if isinstance(child, AxNodeWidget):
                self.nodes.append(child)

    def dock(self, upper: AxNodeWidget, lower: AxNodeWidget):
        lower.move(
            upper.pos().x(),
            upper.pos().y() + upper.rect().height()
        )
        upper.dock_child_widget = lower
        lower.dock_parent_widget = upper

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

            if hot_area.contains(widget.pos()) or hot_area.contains(widget.rect().topRight()):
                self.dock(node, widget)
            else:
                if node == widget.dock_parent_widget:
                    self.undock(node, widget)