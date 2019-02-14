#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import unittest

from atraxiflow.nodes.foundation import Node
from atraxiflow.nodes.common import NullNode


# Test Data
class NodeNoType(Node):
    def run(self, stream):
        pass


class NodeNoRun(Node):
    pass


class test_Node(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def test_node_inheritance(self):
        node = NodeNoRun()
        self.assertRaises(Exception, node.run)

    def test_constructor(self):
        node = NullNode('nodename')
        self.assertEqual('nodename', node.get_name())

        node = NullNode({'hello': 'world'})
        self.assertEqual('', node.get_name())
        self.assertEqual('world', node.get_property('hello'))




if __name__ == '__main__':
    unittest.main()
