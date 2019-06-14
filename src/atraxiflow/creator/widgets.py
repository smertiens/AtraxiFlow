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

    def __init__(self, node: Node, parent=None):
        super().__init__(parent)

        self.node = node
        self.click_pos = QtCore.QPoint(0, 0)

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
        self.raise_()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.move(self.mapToParent(event.pos() - self.click_pos))

        br = self.rect().bottomRight() + self.pos()
        parent_w = br.x() if br.x() > self.parent().width() else self.parent().width()
        parent_h = br.x() if br.y() > self.parent().height() else self.parent().height()
        self.parent().resize(parent_w, parent_h)
