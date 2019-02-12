#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging, os
from common.propertyobject import PropertyObject
from nodes.NullNode import  NullNode
from nodes.FilesystemResource import FilesystemResource

class test_PropertyObject(unittest.TestCase):

    cb_one_run = ''

    def prop_changed_callback(self, data):
        self.cb_one_run = data

    def setUp(self):
        pass

    def tearDown(self):
        cb_one_run = ''

    def get_test_node(self):
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

    def test_variable_scopes(self):
        n = NullNode("demo1", {'d' : 'e'})
        n2 = NullNode("demo2")

        self.assertEqual("demo1", n.get_name())
        self.assertEqual("demo2", n2.get_name())

        self.assertEqual({'d' : 'e'}, n.properties)
        self.assertEqual({}, n2.properties)

        n2.set_property('g', 'h')
        self.assertEqual({'d' : 'e'}, n.properties)
        self.assertEqual({'g': 'h'}, n2.properties)

    def test_all_props_set_correctly(self):
        n = self.get_test_node()
        n.set_property('prop1', 'hello')
        n.set_property('prop2', 'world')
        self.assertTrue(n.check_properties())

        self.assertEqual({'prop1': 'hello', 'prop2': 'world'}, n.properties)
        self.assertEqual('hello', n.get_property('prop1'))
        self.assertEqual('world', n.get_property('prop2'))

    def test_required_props_okay_other_set_by_default(self):
        n = self.get_test_node()
        n.set_property('prop1', 'hello')
        self.assertTrue(n.check_properties())

        self.assertEqual('hello', n.get_property('prop1'))
        self.assertEqual('prop2_default', n.get_property('prop2'))

    def test_required_prop_missing_other_one_there(self):
        n = self.get_test_node()
        n.set_property('prop2', 'hello')
        self.assertFalse(n.check_properties())

        n.set_property('prop1', 'world')
        self.assertTrue(n.check_properties())

    def test_all_props_missing(self):
        n = self.get_test_node()
        self.assertFalse(n.check_properties())

    def test_register_callables(self):
        res = FilesystemResource()
        res.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self.prop_changed_callback)

        self.assertEqual(2, len(res._listeners))

    def test_fire_events(self):
        res = FilesystemResource()
        res.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self.prop_changed_callback)

        self.assertEqual('', self.cb_one_run)
        res.fire_event(PropertyObject.EVENT_PROPERTY_CHANGED, 'hello world')
        self.assertEqual('hello world', self.cb_one_run)

if __name__ == '__main__':
    unittest.main()
