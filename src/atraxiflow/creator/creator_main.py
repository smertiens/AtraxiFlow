#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from PySide2 import QtWidgets
from atraxiflow.creator import main_window
import sys


def launch_app():
    app = QtWidgets.QApplication(sys.argv)
    window = main_window.CreatorMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch_app()
