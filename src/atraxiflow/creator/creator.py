#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging
import sys

import atraxiflow.logging as ax_logging
from PySide2 import QtWidgets
from atraxiflow.creator import main_window


def launch_app():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    window = main_window.CreatorMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    ax_logging.setup_loggers()
    logging.getLogger('creator').debug('Starting up creator...')

    launch_app()
