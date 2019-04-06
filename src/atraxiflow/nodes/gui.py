#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.util import *
from atraxiflow.gui.common import *
from atraxiflow.nodes.common import TextResource
from atraxiflow.nodes.foundation import *


class GUIFormInputNode(InputNode):

    def __init__(self, name="", props=None):

        self._known_properties = {
            'fields': {
                'label': 'Fields',
                'type': 'list',
                'required': True,
                'hint': 'A list of fields to be added to the form',
                'creator:list_item_formatter': self.format_list_item,
                'creator:list_item_fields': [
                    {
                        'name': 'field_name',
                        'label': 'Field name',
                        'type': 'text',
                        'value': ''
                    },
                    {
                        'name': 'label',
                        'label': 'Label',
                        'type': 'text',
                        'value': ''
                    },
                    {
                        'name': 'field_type',
                        'label': 'Field type',
                        'type': 'combobox',
                        'value': ['textfield', 'password', 'textarea', 'checkbox', 'combobox']
                    }
                ],
            },
            'window': {
                'label': 'Window properties',
                'type': 'window_properties',
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
                'type': 'simple_list',
                'items': ['exit', 'continue'],
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

        # initialize widgets here to be able to access them in tests
        self._app = get_qt_app()
        self._wnd = QtWidgets.QDialog()
        self._btn_accept = QtWidgets.QPushButton()
        self._btn_cancel = QtWidgets.QPushButton()

    def format_list_item(self, format, data):
        if format == 'list':
            return '{0} ({1})'.format(data['field_name'], data['field_type'])
        elif format == 'store':
            return data

    def get_output(self):
        '''
        Returns all fields.
        :return: dict
        '''
        return self._results

    def _exec_qt5(self, stream):

        layout = QtWidgets.QGridLayout()
        self._wnd.setLayout(layout)

        def btn_cancel_clicked():
            self._canceled = True
            self._wnd.close()

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

            self._wnd.close()

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
                elif isinstance(data['items'], str):
                    res_result = stream.get_resources(data['items'])

                    if res_result is not None:
                        if not is_iterable(res_result):
                            res_result = [res_result]

                        for resource in res_result:
                            data = resource.get_data()

                            if is_iterable(data):
                                for data_single in data:
                                    elem.addItem(str(data_single))
                            else:
                                elem.addItem(str(data))
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
        self._btn_accept.setText(self.get_property('btn_accept_text'))
        self._btn_accept.connect(QtCore.SIGNAL('clicked()'), btn_accept_clicked)
        self._btn_cancel.setText(self.get_property('btn_cancel_text'))
        self._btn_cancel.connect(QtCore.SIGNAL('clicked()'), btn_cancel_clicked)

        hl = QtWidgets.QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(self._btn_cancel)
        hl.addWidget(self._btn_accept)
        layout.addLayout(hl, row, 1)

        # apply window settings
        wnd_set = self.get_property('window')
        self._wnd.setWindowModality(QtCore.Qt.ApplicationModal)
        self._wnd.setWindowTitle(wnd_set['title'] + ' - AtraxiFlow')

        if wnd_set['width'] != 'auto':
            self._wnd.setFixedWidth(wnd_set['width'])
        if wnd_set['height'] != 'auto':
            self._wnd.setFixedHeight(wnd_set['height'])

        self._wnd.exec_()

    def run(self, stream):
        self.check_properties()
        check_qt5_environment()

        self._exec_qt5(stream)

        if self._canceled:
            if self.get_property('on_cancel') == 'exit':
                return False

        # create text resources for results
        for name, data in self._results.items():
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
                'type': 'simple_list',
                'items': ['info', 'question', 'warning', 'error'],
                'required': False,
                'hint': 'The icon of the dialog (info|question|warning|error)',
                'default': 'info'
            }
        }
        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        # initialize widgets here to be able to access them in tests
        self._app = get_qt_app()
        self._msgbox = QtWidgets.QMessageBox()

    def _exec_qt5(self, stream):

        self._msgbox.setText(self.parse_string(stream, self.get_property('text')))
        # ignored in osx
        self._msgbox.setWindowTitle(self.parse_string(stream, self.get_property('title')))
        self._msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if self.get_property('icon') == 'info':
            self._msgbox.setIcon(QtWidgets.QMessageBox.Information)
        elif self.get_property('icon') == 'question':
            self._msgbox.setIcon(QtWidgets.QMessageBox.Question)
        elif self.get_property('icon') == 'warning':
            self._msgbox.setIcon(QtWidgets.QMessageBox.Warning)
        elif self.get_property('icon') == 'error':
            self._msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        else:
            stream.get_logger().warning(
                'Icon "{0}" not recognized. Try one of these: info, question, warning, error'.format(
                    self.get_property('icon')))
            self._msgbox.setIcon(QtWidgets.QMessageBox.NoIcon)

        self._msgbox.exec_()

    def run(self, stream):
        self.check_properties()
        check_qt5_environment()

        self._exec_qt5(stream)

        return True
