#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import pytest
from atraxiflow.core import *
from atraxiflow.properties import Property
from atraxiflow.exceptions import PropertyException
from atraxiflow.base.resources import *

class MakeResources1Node(Node):

    def __init__(self, properties=None):
        super().__init__({}, properties)

    def run(self, ctx: WorkflowContext) -> bool:
        self.output.add(TextResource('Text 1'))
        self.output.add(TextResource('Text 2'))
        return True

class MakeResources2Node(Node):

    def __init__(self, properties=None):
        super().__init__({}, properties)

    def run(self, ctx: WorkflowContext) -> bool:
        self.output.add(TextResource('Text 3'))
        self.output.add(TextResource('Text 4'))
        return True

class DemoNode(Node):
    """

    @Name: Demo Node
    @Accepts: foo, bar

    """

    def __init__(self, properties=None):
        self.output = Container()
        self.properties = {
            'prop_str': Property(expected_type=str, default='Default value'),
            'prop_bool': Property(expected_type=bool, default=True),
            'prop_list': Property(expected_type=list, default=['Foo', 'Bar']),
            'prop_multi': Property(expected_type=(bool, int), default=False)
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext) -> bool:
        return True

def test_get_properties_from_docstring():

    info = get_node_info(DemoNode)
    assert info['name'] == 'Demo Node'

def test_empty_properties():
    test = DemoNode()
    assert test.property('prop_str').value() == 'Default value'
    assert test.property('prop_bool').value() == True
    assert test.property('prop_list').value() == ['Foo', 'Bar']


def test_multi_type_property():
    test = DemoNode()

    test.property('prop_multi').set_value(True)
    test.property('prop_multi').set_value(123)

    with pytest.raises(ValueError):
        test.property('prop_multi').set_value([])


def test_fill_properties():
    test = DemoNode({
        'prop_str': 'Hello World',
        'prop_bool': False,
        'prop_list': ['my_list']
    })

    assert test.property('prop_str').value() == 'Hello World'
    assert test.property('prop_bool').value() == False
    assert test.property('prop_list').value() == ['my_list']

def test_fail_on_unknown_option():

    with pytest.raises(PropertyException):
        test = DemoNode({
            'prop_unknown': 'Hello World'
        })


def test_add_to_container():

    c1 = Container()
    c2 = Container()

    c1.add(TextResource(''))
    c1.add(TextResource(''))
    assert c1.size() == 2

    c2.add(TextResource(''))
    c2.add(TextResource(''))
    assert c2.size() == 2

    c1.add(c2)
    assert c1.size() == 4

    with pytest.raises(ValueError):
        c1.add("Hello World")

def test_passthru_default():
    
    n1 = MakeResources1Node()
    n2 = MakeResources2Node()

    assert n1.output.size() == 0
    assert n2.output.size() == 0
    assert not n1.get_passthru()

    assert Workflow.create([n1, n2]).run()
    assert n1.output.size() == 2
    assert n2.output.size() == 2

def test_passthru_active():
    
    n1 = MakeResources1Node()
    n2 = MakeResources2Node()
    n1.set_passthru(True)
    n2.set_passthru(True)

    assert n1.output.size() == 0
    assert n2.output.size() == 0
    assert n2.get_passthru()

    assert Workflow.create([n1, n2]).run()
    assert n1.output.size() == 2
    assert n2.output.size() == 4

    