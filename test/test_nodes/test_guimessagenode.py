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

import platform
try:
    from PySide2 import QtWidgets
except ImportError:
    pass

from atraxiflow.core.stream import *
from atraxiflow.nodes.gui import *


def test_gui_messagebox_basics(qtbot, monkeypatch):
    st = Stream()
    st.add_resource(TextResource('greeting', {'text': 'Hello'}))
    out_node = GUIMessageNode({'title': 'Greeting', 'text': '{Text:greeting} World!'})

    monkeypatch.setattr(QtWidgets.QMessageBox, "exec_", lambda *args: QtWidgets.QMessageBox.Yes)

    st.append_node(out_node)
    assert st.flow()

    if platform.system().lower() != 'darwin':
        assert out_node._msgbox.windowTitle() == 'Greeting'

    assert out_node._msgbox.text() == 'Hello World!'
    assert out_node._msgbox.icon() == QtWidgets.QMessageBox.Information


def test_gui_messagebox_icons(qtbot, monkeypatch):
    st = Stream()
    out_node = GUIMessageNode({'title': 'Greeting', 'text': 'Hello World!'})
    st.append_node(out_node)

    monkeypatch.setattr(QtWidgets.QMessageBox, "exec_", lambda *args: QtWidgets.QMessageBox.Yes)

    assert st.flow()
    assert out_node._msgbox.icon() == QtWidgets.QMessageBox.Information

    out_node.set_property('icon', 'question')
    assert st.flow()
    assert out_node._msgbox.icon() == QtWidgets.QMessageBox.Question

    out_node.set_property('icon', 'warning')
    assert st.flow()
    assert out_node._msgbox.icon() == QtWidgets.QMessageBox.Warning

    out_node.set_property('icon', 'error')
    assert st.flow()
    assert out_node._msgbox.icon() == QtWidgets.QMessageBox.Critical
