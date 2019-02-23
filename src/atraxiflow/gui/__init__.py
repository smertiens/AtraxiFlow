#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import sys

from atraxiflow.gui.processing_window import *


class GUI():

    def __init__(self, stream):
        self._stream = stream

    def flow(self):
        app = QtWidgets.QApplication(sys.argv)
        self._stream.set_gui_context(app)

        wnd = ProcessingWindow(self._stream)
        wnd.show()

        app.exec_()
