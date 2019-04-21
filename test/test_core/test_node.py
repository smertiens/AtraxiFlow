#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.core.exceptions import *
from atraxiflow.core.stream import *
from atraxiflow.nodes.common import NullNode
from atraxiflow.nodes.foundation import Node
from atraxiflow.nodes.text import TextResource


# Test Data
class NodeNoType(Node):
    def run(self, stream):
        pass


class NodeNoRun(Node):
    pass


class InputTestingNode(Node):

    def __init__(self, name="", props=None):
        self._known_properties = {

        }

        self._known_inputs = {
            'input1': {
                'required': True,
                'accepts': [TextResource]
            },
            'input2': {
                'limit': 0,
                'required': False,
                'accepts': [TextResource]
            }
        }

        self._listeners = {}
        self._inputs = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        self._out = []

    def get_output(self):
        return self._out

    def run(self, stream):
        self.check_properties()
        self.check_inputs()

        return True


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


def test_set_input_has_input():
    stream = Stream()
    node = InputTestingNode()
    res = TextResource({'msg': 'Hi'})

    assert not node.has_input('input1')

    node.connect(res, 'input1')

    assert node.has_input('input1')

    assert stream >> node >> flow()


def test_set_input_wrong():
    stream = Stream()
    node = InputTestingNode()
    res = TextResource({'msg': 'Hi'})

    with pytest.raises(InputException):
        node.connect(res, 'not_existing_input')


def test_get_input():
    stream = Stream()
    node = InputTestingNode()
    res = TextResource({'msg': 'Hi'})
    node.connect(res, 'input1')

    assert node.has_input('input1')
    result = node.get_input('input1')
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == res


def test_fail_on_missing_required_input():
    stream = Stream()
    node = InputTestingNode()

    with pytest.raises(InputException):
        stream >> node >> flow()


def test_replace_input_when_limit_reached():
    stream = Stream()
    node = InputTestingNode()
    res1 = TextResource({'msg': 'Hi'})
    node.connect(res1, 'input1')

    assert node.has_input('input1')
    assert len(node.get_input('input1')) == 1
    assert node.get_input('input1')[0] == res1

    res2 = TextResource({'msg': 'Hi'})
    node.connect(res2, 'input1')

    assert node.has_input('input1')
    assert len(node.get_input('input1')) == 1
    assert node.get_input('input1')[0] == res2


def test_add_multiple_inputs():
    stream = Stream()
    node = InputTestingNode()
    res1 = TextResource({'msg': 'Hi'})
    res2 = TextResource({'msg': 'Hi'})
    res3 = TextResource({'msg': 'Hi'})
    node.connect(res1, 'input2')
    node.connect(res2, 'input2')
    node.connect(res3, 'input2')

    assert node.has_input('input2')
    assert len(node.get_input('input2')) == 3
    result = node.get_input('input2')

    assert res1 in result
    assert res2 in result
    assert res2 in result


def test_disconnect_input():
    stream = Stream()
    node = InputTestingNode()
    res1 = TextResource({'msg': 'Hi'})
    res2 = TextResource({'msg': 'Hi'})
    node.connect(res1, 'input2')
    node.connect(res2, 'input2')

    assert node.has_input('input2')
    assert len(node.get_input('input2')) == 2

    node.disconnect('input2', res1)
    assert node.has_input('input2')
    assert len(node.get_input('input2')) == 1

    node.disconnect('input2', res2)
    assert not node.has_input('input2')
    assert len(node.get_input('input2')) == 0


def test_disconnect_all_on_input():
    stream = Stream()
    node = InputTestingNode()
    res1 = TextResource({'msg': 'Hi'})
    res2 = TextResource({'msg': 'Hi'})
    node.connect(res1, 'input2')
    node.connect(res2, 'input2')

    assert node.has_input('input2')
    assert len(node.get_input('input2')) == 2
    node.disconnect('input2')
    assert not node.has_input('input2')
    assert len(node.get_input('input2')) == 0


def test_disconnect_all():
    stream = Stream()
    node = InputTestingNode()
    res1 = TextResource({'msg': 'Hi'})
    res2 = TextResource({'msg': 'Hi'})
    node.connect(res1, 'input1')
    node.connect(res2, 'input2')

    assert node.has_input('input1')
    assert node.has_input('input2')

    node.disconnect()

    assert node._inputs == {}
