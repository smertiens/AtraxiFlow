#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import unittest

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode


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

        self.assertTrue(st.flow())


if __name__ == '__main__':
    unittest.main()
