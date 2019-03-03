#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os
import pytest

if 'TRAVIS_TEST' in os.environ and os.environ['TRAVIS_TEST'] == 'yes':
    pytest.skip("Skipping gui tests when running on travis ci", allow_module_level=True)

try:
    from PySide2 import QtWidgets
except ImportError:
    pass

from atraxiflow.core.stream import *
from atraxiflow.nodes.gui import *


def test_basics(qtbot, monkeypatch):
    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'greeting': Combobox('Greeting', items=['Hello', 'Cheerio']),
            'name': Textfield('Name')
        },
        'text': 'How should I greet you?',
        'window': Window(title='Greeting')
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()
    assert form_node._wnd.windowTitle() == 'Greeting - AtraxiFlow'

    widgets = form_node._wnd.findChildren(QtWidgets.QWidget)

    label_count = 0
    other_count = 0
    btn_count = 0
    for w in widgets:
        if isinstance(w, QtWidgets.QLabel):
            label_count += 1
            assert w.text() == 'Greeting' or w.text() == 'Name' or w.text() == 'How should I greet you?'
        elif isinstance(w, QtWidgets.QLineEdit):
            other_count += 1
        elif isinstance(w, QtWidgets.QComboBox):
            other_count += 1
        elif isinstance(w, QtWidgets.QPushButton):
            btn_count += 1

    assert label_count == 3
    assert other_count == 2
    assert btn_count == 2


def test_exception_on_unrecognized_field(qtbot, monkeypatch):
    class Something():
        pass

    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'name': Something()
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    with pytest.raises(GUIException):
        st.flow()

    form_node.set_property('fields', {
        'name': {
            'type': 'Sometype',
            'label': 'Demo'
        }
    })

    with pytest.raises(GUIException):
        st.flow()

    form_node.set_property('fields', {
        'name': Textfield('Hello')
    })

    assert st.flow()


def test_field_text(qtbot, monkeypatch):
    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'name': Textfield('Demo', 'field value')
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()

    expected_widgets = 0
    for w in form_node._wnd.findChildren(QtWidgets.QWidget):
        if isinstance(w, QtWidgets.QLabel):
            assert w.text() == 'Demo'
            expected_widgets += 1
        elif isinstance(w, QtWidgets.QLineEdit):
            assert w.text() == 'field value'
            expected_widgets += 1

    assert expected_widgets == 2


def test_field_password(qtbot, monkeypatch):
    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'name': Password('Demo', 'field value')
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()

    expected_widgets = 0
    for w in form_node._wnd.findChildren(QtWidgets.QLineEdit):
        assert w.text() == 'field value'
        assert w.echoMode() == QtWidgets.QLineEdit.Password
        expected_widgets = 1

    assert expected_widgets == 1


def test_field_textarea(qtbot, monkeypatch):
    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'name': Textarea('Demo', 'field value')
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()

    expected_widgets = 0
    for w in form_node._wnd.findChildren(QtWidgets.QTextEdit):
        assert w.document().toPlainText() == 'field value'
        expected_widgets = 1

    assert expected_widgets == 1


def test_field_checkbox(qtbot, monkeypatch):
    st = Stream()
    form_node = GUIFormInputNode({
        'fields': {
            'name': Checkbox('Hello', True)
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()

    expected_widgets = 0
    for w in form_node._wnd.findChildren(QtWidgets.QCheckBox):
        assert w.isChecked()
        expected_widgets = 1

    assert expected_widgets == 1


def test_field_combobox_simple(qtbot, monkeypatch):
    st = Stream()
    items_expected = ['Item 1', 'Item 2', 'Item 3']
    form_node = GUIFormInputNode({
        'fields': {
            'name': Combobox('Hello', items_expected, selected='Item 2')
        }
    })
    st.append_node(form_node)
    qtbot.addWidget(form_node._wnd)

    monkeypatch.setattr(QtWidgets.QMainWindow, "show", lambda *args: [])

    assert st.flow()

    expected_widgets = 0
    for w in form_node._wnd.findChildren(QtWidgets.QComboBox):
        assert w.currentIndex() == 1

        items = []
        for i in range(0, 3):
            items.append(w.itemText(i))

        assert items == items_expected
        expected_widgets = 1

    assert expected_widgets == 1
