import unittest, logging
from nodes.Node import Node
from Stream import Stream


# Test Data
class NodeNoType(Node):
    def run(self, stream):
        pass


class NodeNoRun(Node):
    def getNodeClass(self):
        return 'NodeNoRun'


class NodeProps(Node):
    _known_properties = {
        'hello': {
            'required': True,
            'hint': 'Demo1',
            'default': ''
        },
        'world': {
            'required': False,
            'hint': 'Demo2',
            'default': 'defaultValue'
        }
    }

    def getNodeClass(self):
        return 'NodeProps'

    def run(self, stream):
        pass


class test_Node(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)


    def test_node_inheritance(self):
        node = NodeNoType()
        self.assertRaises(Exception, node.getNodeClass)

        node = NodeNoRun()
        self.assertRaises(Exception, node.run)

    def test_prop_merge(self):
        test = {'hello': 'world'}
        node = NodeProps("Node", test)

        print (node.properties)

    def test_prop_set_at_init(self):
        test = {'hello': 'world', 'world':'heythere'}
        node = NodeProps("Node", test)
        node.mergeProperties()
        self.assertEqual(test, node.properties)

    def test_prop_get_set(self):
        node = NodeProps("Node")
        node.setProperty('hello', 'world')
        self.assertEqual(node.getProperty('hello'), 'world')

    def test_node_known_props(self):
        st = Stream()

        # should be okay
        node = NodeProps("Node", {'hello': 'world'})
        node.mergeProperties()
        self.assertFalse(node.hasErrors)

        # missing
        node = NodeProps("Node", {'world': ''})
        node.mergeProperties()
        self.assertTrue(node.hasErrors)

        # set default
        node = NodeProps("Node", {'hello': 'required'})
        node.mergeProperties()
        self.assertFalse(node.hasErrors)
        self.assertEqual(node.getProperty('world'), 'defaultValue')


if __name__ == '__main__':
    unittest.main()
