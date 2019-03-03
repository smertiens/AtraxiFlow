#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

'''
Contains common UI functions
'''

import threading

from atraxiflow.core.data import StringValueProcessor
from atraxiflow.core.stream import *
from atraxiflow.gui.processing_window import *


class GUIStream():
    '''
    Provide the user with a simple user interface
    '''

    def __init__(self):
        self._stream = None
        self._autostart = False

    @staticmethod
    def from_stream(stream):
        '''
        :param stream: The stream to wrap
        :type stream: Stream
        :rtype: GUIStream
        '''
        inst = GUIStream()
        inst.set_stream(stream)
        return inst

    def set_stream(self, stream):
        '''
        Set the stream to run

        :type stream: Stream
        :return: None
        '''
        self._stream = stream

    def set_autostart(self, val):
        '''
        If true will automatically start the stream after the ui has been loaded

        :type val: bool
        :return: None
        '''
        self._autostart = val

    def flow(self):
        '''
        Start the ui

        :return: None
        '''
        if self._stream is None:
            raise ExecutionException(
                'No stream set for GUIStream. Use GUIStream.from_stream() or instance.set_strea().')

        app = QtWidgets.QApplication.instance() if QtWidgets.QApplication.instance() is not None else QtWidgets.QApplication()
        self._stream.set_gui_context(app)

        wnd = ProcessingWindow(self._stream, self._autostart)
        wnd.show()

        app.exec_()


class FormField:
    '''
    Parent class for form fields
    '''

    def resolve(self, stream):
        '''
        Resolve variables using :py:class:`StringValueProcessor`

        :type stream: Stream
        :return: The configuration values for the form field
        :rtype: dict
        '''
        processor = StringValueProcessor(stream)

        for key, value in self._data.items():
            if key in self._resolve_fields:
                self._data[key] = processor.parse(value)

        return self._data


class Textfield(FormField):
    '''
    A simple text field

    :param label: The label for the input
    :type label: str
    :param value: The default value to set when showing the form
    :type value: str

    :return: The configuration values for the form field
    :rtype: dict
    '''

    def __init__(self, label, value=""):
        self._resolve_fields = ['value', 'label']
        self._data = {
            'type': 'textfield',
            'label': label,
            'value': value
        }


class Textarea(FormField):
    '''
    A larger text field supporting rich text input

    :param label: The label for the input
    :type label: str
    :param value: The default value to set when showing the form
    :type value: str

    :return: The configuration values for the form field
    :rtype: dict
    '''

    def __init__(self, label, value=""):
        self._resolve_fields = ['value', 'label']
        self._data = {
            'type': 'textarea',
            'label': label,
            'value': value
        }


class Combobox(FormField):
    '''
    A simple combobox

    :param label: The label for the input
    :type label: str
    :param items: The items to add to the combobox or a resource query to retrieve a list of strings
    :type items: dict, list, str
    :param selected: The value or key of the default item
    :type selected: str
    :param editable: Determines wether the user can enter custom values
    :type editable: bool

    :return: The configuration values for the form field
    :rtype: dict
    '''
    def __init__(self, label, items=None, selected=None, editable=False):
        self._resolve_fields = ['value', 'label']
        self._data = {
            'type': 'combobox',
            'label': label,
            'items': items,
            'selected': selected,
            'editable': editable
        }


class Password(FormField):
    '''
    A textfield that masks it's input with '*'

    :param label: The label for the input
    :type label: str
    :param value: The default value to set when showing the form
    :type value: str

    :return: The configuration values for the form field
    :rtype: dict
    '''
    def __init__(self, label, value=""):
        self._resolve_fields = ['value', 'label']
        self._data = {
            'type': 'password',
            'label': label,
            'value': value
        }


class Checkbox(FormField):
    '''
    A checkbox

    :param label: The label for the input
    :type label: str
    :param value: The default value to set when showing the form
    :type value: bool

    :return: The configuration values for the form field
    :rtype: dict
    '''
    def __init__(self, label, value=False):
        self._resolve_fields = ['label']
        self._data = {
            'type': 'checkbox',
            'label': label,
            'value': value
        }


def Window(title='New Window', width='auto', height='auto', resizable=False):
    '''
    Return a basic config for new windows

    :param title: The window title
    :type title: str
    :param width: Width of the window at startup
    :type width: int
    :param height: Height of the window at startup
    :type height: int
    :param resizable: Wether the user can resize the window
    :type resizable: bool
    :rtype: dict
    '''
    return {
        'title': title,
        'width': width,
        'height': height,
        'resizable': resizable  # not used yet
    }


def check_qt5_environment():
    '''
    Checks whether qt5 can be safely run and raises EnvironmentException if necessary
    '''

    try:
        from PySide2 import QtCore
    except ImportError:
        raise EnvironmentException('No PySide2 detected. Install via "pip install pyside2".')

    if threading.current_thread() is not threading.main_thread():
        raise EnvironmentException('Qt5 GUI nodes can not be run from a stream-branch.')
