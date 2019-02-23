#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import threading

from atraxiflow.core.exceptions import *
from atraxiflow.core.data import StringValueProcessor

class FormField:

    def resolve(self, stream):
        fieldsToResolve = ['value']
        processor = StringValueProcessor(stream)

        for key, value in self._data.items():
            if key in fieldsToResolve:
                self._data[key] = processor.parse(value)

        return self._data


class Textfield(FormField):
    def __init__(self, label, value=""):
        self._data = {
            'type': 'textfield',
            'label': label,
            'value': value
        }

class Textarea(FormField):
    def __init__(self, label, value=""):
        self._data = {
            'type': 'textarea',
            'label': label,
            'value': value
        }

class Combobox(FormField):
    def __init__(self, label, items=None, selected=None, editable=False):
        self._data = {
            'type': 'combobox',
            'label': label,
            'items': items,
            'selected': selected,
            'editable': editable
        }


class Password(FormField):
    def __init__(self, label, value=""):
        self._data = {
            'type': 'password',
            'label': label,
            'value': value
        }


def window(title='New Window', width='auto', height='auto', resizable=False):
    return {
        'title': title,
        'width': width,
        'height': height,
        'resizable': resizable  # not used yet
    }


def check_qt5_environment():
    '''
    Checks wether qt5 can be savely run and raises EnvironmentException if necessary
    '''

    try:
        from PySide2 import QtCore
    except ImportError:
        raise EnvironmentException('No PySide2 detected. Install via "pip install pyside2".')

    if threading.current_thread() is not threading.main_thread():
        raise EnvironmentException('Qt5 GUI nodes can not be run from a stream-branch.')
