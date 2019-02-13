#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging
from atraxiflow.nodes.foundation import Node


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


if __name__ == '__main__':
    unittest.main()
