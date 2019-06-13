#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from PySide2 import QtCore, QtWidgets, QtGui
from atraxiflow.core import Node

class AxNodeWidget(QtWidgets.QWidget):

    def __init__(self, node: Node, parent=None):
        super().__init__(parent)

        self.node = node
        self.click_pos = QtCore.QPoint(0, 0)

        self.setLayout(QtWidgets.QVBoxLayout())

        # Title
        self.title_label = QtWidgets.QLabel('Demo')
        # self.title_label.setStyleSheet('border-bottom: 1px solid black')
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.title_label.setCursor(QtCore.Qt.SizeAllCursor)

        # Content wrapper
        self.content_wrapper = QtWidgets.QWidget(self)
        self.content_wrapper.setStyleSheet('background: white; border: none;')
        self.content_wrapper.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Default content
        label = QtWidgets.QLabel(self.content_wrapper)
        label.setText('No options provided')
        label.move(self.content_wrapper.width() / 2, 20)

        # Add to window
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.title_label)
        #self.layout().addWidget(self.content_wrapper)
        self.setStyleSheet('border: 1px solid black; background:lightgray')

        self.build_node_ui()

        self.resize(300, 150)

    def build_node_ui(self):
        if hasattr(self.node, 'get_ui'):
            widget = self.node.get_ui()
        else:
            widget = QtWidgets.QWidget()

        widget.setLayout(QtWidgets.QFormLayout())
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # build default widget
        for name, prop in self.node.get_properties().items():
            label = prop.get_label() if prop.get_label() != '' else name

            if prop.get_expected_type()[0] == str:
                control = QtWidgets.QLineEdit()
            elif prop.get_expected_type()[0] == bool:
                control = QtWidgets.QCheckBox()
            elif prop.get_expected_type()[0] == list:
                control = QtWidgets.QListWidget()
            else:
                raise Exception('Unrecognized type: %s' % prop.get_expected_type()[0])

            widget.layout().addRow(label, control)

        self.layout().addWidget(widget)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.click_pos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        print(event.localPos())
        x = event.x() - self.x()
        y = event.y() - self.y()

        self.move(self.mapToParent(event.pos() - self.click_pos))

        br = self.rect().bottomRight() + self.pos()
        parent_w = br.x() if br.x() > self.parent().width() else self.parent().width()
        parent_h = br.x() if br.y() > self.parent().height() else self.parent().height()
        self.parent().resize(parent_w, parent_h)
