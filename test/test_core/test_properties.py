#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.properties import PropertyObject
from atraxiflow.nodes.common import NullNode
from atraxiflow.nodes.filesystem import FilesystemResource

cb_one_run = ''


def prop_changed_callback(data):
    cb_one_run = data


def get_test_node():
    n = NullNode("test")
    n._known_properties = {
        'prop1': {
            'label': "",
            'type': "string",
            'required': True,
            'hint': '',
            'default': "prop1_default",
            'primary': True
        },
        'prop2': {
            'label': "",
            'type': "string",
            'required': False,
            'hint': '',
            'default': "prop2_default"
        }
    }

    return n


def test_variable_scopes():
    n = NullNode("demo1", {'d': 'e'})
    n2 = NullNode("demo2")

    assert "demo1" == n.get_name()
    assert "demo2" == n2.get_name()

    assert {'d': 'e'} == n.properties
    assert {} == n2.properties

    n2.set_property('g', 'h')
    assert {'d': 'e'} == n.properties
    assert {'g': 'h'} == n2.properties


def test_all_props_set_correctly():
    n = get_test_node()
    n.set_property('prop1', 'hello')
    n.set_property('prop2', 'world')
    assert n.check_properties()

    assert {'prop1': 'hello', 'prop2': 'world'} == n.properties
    assert 'hello' == n.get_property('prop1')
    assert 'world' == n.get_property('prop2')


def test_required_props_okay_other_set_by_default():
    n = get_test_node()
    n.set_property('prop1', 'hello')
    assert n.check_properties()

    assert 'hello' == n.get_property('prop1')
    assert 'prop2_default' == n.get_property('prop2')


def test_required_prop_missing_other_one_there():
    n = get_test_node()
    n.set_property('prop2', 'hello')
    assert not n.check_properties()

    n.set_property('prop1', 'world')
    assert n.check_properties()


def test_all_props_missing():
    n = get_test_node()
    assert not n.check_properties()


def test_register_callables():
    res = FilesystemResource()
    res.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, prop_changed_callback)

    assert 2 == len(res._listeners)


def test_fire_events():
    res = FilesystemResource()
    res.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, prop_changed_callback)

    assert '' == cb_one_run
    res.fire_event(PropertyObject.EVENT_PROPERTY_CHANGED, 'hello world')
    assert 'hello world', cb_one_run
