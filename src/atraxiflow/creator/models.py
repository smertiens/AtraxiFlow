#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from typing import Any, Dict
from atraxiflow.core import Node
from PySide2 import QtCore, QtGui, QtWidgets


class AxNodeTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, node_data: Dict[str, list]):
        super().__init__()
        self._ptr = None
        self._node_data = node_data

        self.rows = 0
        for group, data in self._node_data.items():
            self.rows += len(data)

        print(self.rows)

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = ...) -> QtCore.QModelIndex:
        return self.createIndex(row, column, self._ptr)

    def parent(self, child: QtCore.QModelIndex):
        return QtCore.QModelIndex()

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return self.rows

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 1

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        return 'Test'
