import unittest, logging
from nodes.Node import Node
from Stream import Stream

# Test Data
class NodeNoType(Node):
    def run(self, stream):
        pass

class NodeNoRun(Node):
    def getNodeType(self):
        return 'NodeNoRun'

class NodeProps(Node):

    _known_properties = {
        'hello' : {
            'required' : True,
            'hint': 'Demo1',
            'default': ''
        },
        'world' : {
            'required' : False,
            'hint': 'Demo2',
            'default': 'defaultValue'
        }
    }
    def getNodeType(self):
        return 'NodeProps'
    def run(self, stream):
        pass


class test_Node(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def test_node_inheritance(self):
        node = NodeNoType()
        self.assertRaises(Exception, node.getNodeType)

        node = NodeNoRun()
        self.assertRaises(Exception, node.run)

    def test_prop_set_at_init(self):
        test = {'hello' : 'world'}
        node = NodeProps(test)
        self.assertEqual(test, node.properties)

    def test_prop_get_set(self):
        node = NodeProps()
        node.setProperty('hello', 'world')
        self.assertEqual(node.getProperty('hello'), 'world')

    def test_node_known_props(self):
        st = Stream()

        # should be okay
        node = NodeProps({'hello': 'world'})
        node.checkProperties()
        self.assertFalse(node.hasErrors)

        # missing
        node = NodeProps({'world', ''})
        node.checkProperties()
        self.assertTrue(node.hasErrors)

        # set default
        node = NodeProps({'hello': 'required'})
        node.checkProperties()
        self.assertFalse(node.hasErrors)
        self.assertEqual(node.getProperty('world'), 'defaultValue')


if __name__ == '__main__':
    unittest.main()