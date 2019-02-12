#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging, os
from Stream import Stream
from nodes.EchoOutputNode import EchoOutputNode


class test_EchoOutputNode(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def test_create_node(self):
        st = Stream()
        n = EchoOutputNode('demo', {'msg': 'hello world'})

        self.assertEqual('hello world', n.get_property('msg'))

    def test_run(self):
        st = Stream()
        n = EchoOutputNode()
        n.set_property('msg', 'Hello World')
        st.append_node(n)

        self.assertTrue(st.run())


if __name__ == '__main__':
    unittest.main()
