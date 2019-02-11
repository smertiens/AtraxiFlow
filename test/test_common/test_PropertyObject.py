import unittest, logging, os
from common.propertyobject import PropertyObject
from nodes.NullNode import  NullNode

class test_PropertyObject(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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


if __name__ == '__main__':
    unittest.main()
