#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.nodes.common import CLIInputNode
from atraxiflow.core.stream import *

def test_create():
    node = CLIInputNode('node', {'prompt': 'Hello', 'save_to': 'world'})
    assert 'Hello' == node.get_property('prompt')
    assert 'world' == node.get_property('save_to')
