#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging

from PySide2 import QtWidgets, QtCore


class LogboxFormatter(logging.Formatter):

    def format(self, record):
        super().format(record)
        return '{0} {1}: {2}'.format(self.formatTime(record, '%H:%M:%S'), record.module, record.getMessage())

class Qt5TextEditHandler(logging.Handler):

    def __init__(self, txt):
        super().__init__()
        self._textedit = txt

    def emit(self, record):
        '''

        :type record: logging.LogRecord
        '''

        msg = self._textedit.document().toHtml()

        styles = 'color:black'
        if record.levelno == logging.WARNING:
            styles = 'color:chocolate'
        elif record.levelno == logging.DEBUG:
            styles = 'color:gray'
        elif record.levelno >= logging.WARNING:
            styles = 'color:red'

        msg += '<span style="{0}">{1}</span>'.format(styles, self.format(record))
        self._textedit.document().setHtml(msg)


class ProcessingWindow(QtWidgets.QMainWindow):

    def __init__(self, stream, autostart = False, parent=None):
        super(ProcessingWindow, self).__init__(parent)

        self._stream = stream
        self.setWindowTitle('AtraxiFlow')
        self.setFixedWidth(400)

        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.hbox_header = QtWidgets.QHBoxLayout()
        self.label_logo = QtWidgets.QLabel('AtraxiFlow')
        self.label_logo.setStyleSheet("font-family: sans-serif; font-size:24px")
        self.label_version = QtWidgets.QLabel('')
        self.label_version.setStyleSheet("font-size:10px")
        self.btn_start = QtWidgets.QPushButton('Run')
        self.btn_start.connect(QtCore.SIGNAL('clicked()'), lambda: self._stream.flow())
        self.hbox_header.addWidget(self.label_logo)
        self.hbox_header.addWidget(self.label_version, alignment=QtCore.Qt.AlignBottom)
        self.hbox_header.addWidget(self.btn_start)
        self.layout.addLayout(self.hbox_header)

        self.text_logbox = QtWidgets.QTextEdit()
        self.text_logbox.setReadOnly(True)
        self.layout.addWidget(self.text_logbox)

        self.progressbar = QtWidgets.QProgressBar()
        self.layout.addWidget(self.progressbar)

        self.text_logbox.setText('<span style="color:black">Welcome to AtraxiFlow!</span>')

        self._run_stream()

        if autostart is True:
            self._stream.flow()

    def _run_stream(self):
        # set up log handler
        hdlr = Qt5TextEditHandler(self.text_logbox)
        hdlr.setFormatter(LogboxFormatter())
        hdlr.setLevel(logging.DEBUG)

        self._stream.get_logger().addHandler(hdlr)
        self._stream.get_logger().setLevel(logging.DEBUG)
        logging.getLogger('root').addHandler(hdlr)
        logging.getLogger('root').setLevel(logging.DEBUG)

        # set up progress bar
        def update_progressbar(data):
            self.progressbar.setValue(self.progressbar.value() + 1)
            self.progressbar.repaint()

        self.progressbar.setMaximum(self._stream.get_node_count())
        self.progressbar.setValue(0)
        self._stream.add_listener(self._stream.EVENT_NODE_FINISHED, update_progressbar)
