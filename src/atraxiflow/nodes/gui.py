#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.gui import *
from atraxiflow.nodes.common import TextResource
from atraxiflow.nodes.foundation import *


class GUIFormInputNode(InputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'fields': {
                'label': 'Fields',
                'type': 'list',
                'required': True,
                'hint': 'A list of fields to be added to the form'
            },
            'window': {
                'label': 'Window properties',
                'type': 'list',
                'required': False,
                'hint': 'A list of properties for the GUI window',
                'default': Window()
            },
            'text': {
                'label': 'Text',
                'type': 'string',
                'required': False,
                'hint': 'A description text for the form',
                'default': ''
            },
            'btn_cancel_text': {
                'label': 'Cancel button text',
                'type': 'string',
                'required': False,
                'hint': 'The text of the cancel button',
                'default': 'Cancel'
            },
            'btn_accept_text': {
                'label': 'Accept button text',
                'type': 'string',
                'required': False,
                'hint': 'The text of the accept button',
                'default': 'Okay'
            },
            'on_cancel': {
                'label': 'Cancel action',
                'type': 'string',
                'required': False,
                'hint': 'The action to take when the user cancels the dialog.',
                'default': 'exit'
            }
        }
        self._listeners = {}
        self._controls = {}
        self._results = {}

        self._canceled = False

        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_data(self):
        '''
        Returns all fields.
        :return: dict
        '''
        return self._results

    def _exec_qt5(self, stream):
        from PySide2 import QtWidgets, QtCore

        app = None
        reuse_app = False
        if isinstance(stream.get_gui_context(), QtWidgets.QApplication):
            app = stream.get_gui_context()
            reuse_app = True
        else:
            app = QtWidgets.QApplication()

        wnd = QtWidgets.QDialog()
        layout = QtWidgets.QGridLayout()
        wnd.setLayout(layout)

        def btn_cancel_clicked():
            self._canceled = True
            wnd.close()

        def btn_accept_clicked():
            for name, widget in self._controls.items():
                if isinstance(widget, QtWidgets.QLineEdit):
                    self._results[name] = widget.text()
                elif isinstance(widget, QtWidgets.QComboBox):
                    self._results[name] = widget.currentText()
                elif isinstance(widget, QtWidgets.QTextEdit):
                    self._results[name] = widget.toPlainText()
                elif isinstance(widget, QtWidgets.QCheckBox):
                    self._results[name] = widget.isChecked()

            wnd.close()

        row = 0
        if self.get_property('text') != '':
            self.label_text = QtWidgets.QLabel(self.get_property('text'))
            layout.addWidget(self.label_text, row, 0, columnSpan=2)
            row = 1

        for name, control in self.get_property('fields').items():
            data = {}
            if not isinstance(control, dict):
                if not hasattr(control, 'resolve'):
                    raise GUIException(
                        'Invalid field data. Must be dict or one of the convenience functions (e.g. textfield().')
                else:
                    data = control.resolve(stream)
            else:
                data = control

            elem_label = QtWidgets.QLabel(data['label'])
            elem = None

            if data['type'] == 'textfield' or data['type'] == 'password':
                elem = QtWidgets.QLineEdit()
                if data['type'] == 'password':
                    elem.setEchoMode(QtWidgets.QLineEdit.Password)
                elem.setText(data['value'])

                layout.addWidget(elem_label, row, 0)
                layout.addWidget(elem, row, 1)

            elif data['type'] == 'textarea':
                elem = QtWidgets.QTextEdit()
                elem.setText(data['value'])

                layout.addWidget(elem_label, row, 0, QtCore.Qt.AlignTop)
                layout.addWidget(elem, row, 1)

            elif data['type'] == 'checkbox':
                elem = QtWidgets.QCheckBox()
                elem.setChecked(data['value'] is True)

                layout.addWidget(elem_label, row, 0, QtCore.Qt.AlignTop)
                layout.addWidget(elem, row, 1)

            elif data['type'] == 'combobox':
                elem = QtWidgets.QComboBox()
                elem.setEditable(data['editable'] is True)

                if isinstance(data['items'], dict):
                    for key, value in data['items'].items():
                        elem.addItem(value, key)

                        if key == data['selected']:
                            elem.setCurrentIndex(elem.count() - 1)

                elif isinstance(data['items'], list):
                    for value in data['items']:
                        elem.addItem(value)

                        if value == data['selected']:
                            elem.setCurrentIndex(elem.count() - 1)
                else:
                    raise GUIException("Invalid item-list format for combobox. Expected dict or list.")

                layout.addWidget(elem_label, row, 0)
                layout.addWidget(elem, row, 1)

            # Register element
            if elem is not None:
                self._controls[name] = elem
            else:
                raise GUIException("Unknown control: {0}".format(data['type']))

            row += 1

        # Add buttons to layout
        btn_accept = QtWidgets.QPushButton(self.get_property('btn_accept_text'))
        btn_accept.connect(QtCore.SIGNAL('clicked()'), btn_accept_clicked)
        btn_cancel = QtWidgets.QPushButton(self.get_property('btn_cancel_text'))
        btn_cancel.connect(QtCore.SIGNAL('clicked()'), btn_cancel_clicked)

        hl = QtWidgets.QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(btn_cancel)
        hl.addWidget(btn_accept)
        layout.addLayout(hl, row, 1)

        # apply window settings
        wnd_set = self.get_property('window')
        wnd.setWindowTitle(wnd_set['title'] + ' - AtraxiFlow')

        if wnd_set['width'] != 'auto':
            wnd.setFixedWidth(wnd_set['width'])
        if wnd_set['height'] != 'auto':
            wnd.setFixedHeight(wnd_set['height'])

        if not reuse_app:
            wnd.show()
            app.exec_()
        else:
            wnd.exec_()

    def run(self, stream):
        self.check_properties()
        check_qt5_environment()

        self._exec_qt5(stream)

        if self._canceled:
            if self.get_property('on_cancel') == 'exit':
                return False

        # create text resources for results
        for name, data in self.get_data().items():
            stream.add_resource(TextResource(name, {'text': data}))

        return True


class GUIMessageNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'title': {
                'label': 'Title',
                'type': 'string',
                'required': False,
                'hint': 'The title of the dialog',
                'default': ''
            },
            'text': {
                'label': 'Text',
                'type': 'string',
                'required': False,
                'hint': 'The message of the dialog',
                'default': ''
            },
            'icon': {
                'label': 'Icon',
                'type': 'string',
                'required': False,
                'hint': 'The icon of the dialog (info|question|warning|error)',
                'default': 'info'
            }
        }
        self._listeners = {}

        self.name, self.properties = self.get_properties_from_args(name, props)

    def _exec_qt5(self, stream):
        from PySide2 import QtWidgets

        app = None
        reuse_app = False
        if isinstance(stream.get_gui_context(), QtWidgets.QApplication):
            app = stream.get_gui_context()
            reuse_app = True
        else:
            app = QtWidgets.QApplication()

        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(self.parse_string(stream, self.get_property('text')))
        msgbox.setWindowTitle(self.parse_string(stream, self.get_property('title')))
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if self.get_property('icon') == 'info':
            msgbox.setIcon(QtWidgets.QMessageBox.Information)
        elif self.get_property('icon') == 'question':
            msgbox.setIcon(QtWidgets.QMessageBox.Question)
        elif self.get_property('icon') == 'warning':
            msgbox.setIcon(QtWidgets.QMessageBox.Warning)
        elif self.get_property('icon') == 'error':
            msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        else:
            stream.get_logger().warning(
                'Icon "{0}" not recognized. Try one of these: info, question, warning, error'.format(
                    self.get_property('icon')))
            msgbox.setIcon(QtWidgets.QMessageBox.NoIcon)

        if not reuse_app:
            app.exec_()

        msgbox.exec_()

    def run(self, stream):
        self.check_properties()
        check_qt5_environment()

        self._exec_qt5(stream)

        return True
