#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import builtins
from atraxiflow.nodes.common import CLIInputNode
from atraxiflow.core.stream import *
from atraxiflow.nodes.text import *


def test_create():
    node = CLIInputNode('node', {'prompt': 'Hello', 'save_to': 'world'})
    assert 'Hello' == node.get_property('prompt')
    assert 'world' == node.get_property('save_to')


def test_output(monkeypatch):
    def input_mock(prompt):
        return 'Hello World'

    monkeypatch.setattr(builtins, 'input', input_mock)

    st = Stream()
    node = CLIInputNode('node', {'prompt': 'Hello', 'save_to': 'world'})
    st.append_node(node)
    assert st.flow()

    out = node.get_output()
    assert isinstance(out, TextResource)
    assert out.get_data() == 'Hello World'
    assert out == st.get_resources('Text:world')[0]
