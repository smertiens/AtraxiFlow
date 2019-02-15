#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.nodes.common import NullNode
from atraxiflow.nodes.foundation import Node


# Test Data
class NodeNoType(Node):
    def run(self, stream):
        pass


class NodeNoRun(Node):
    pass


def test_node_inheritance():
    node = NodeNoRun()

    with pytest.raises(Exception):
        node.run()


def test_constructor():
    node = NullNode('nodename')
    assert 'nodename' == node.get_name()

    node = NullNode({'hello': 'world'})
    assert '' == node.get_name()
    assert 'world' == node.get_property('hello')
