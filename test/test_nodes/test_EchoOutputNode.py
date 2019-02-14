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
from atraxiflow.nodes.filesystem import FilesystemResource
from atraxiflow.nodes.text import TextResource

class test_EchoOutputNode(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def test_create_node(self):
        st = Stream()
        n = EchoOutputNode('demo', {'msg': 'hello world'})

        self.assertEqual('hello world', n.get_property('msg'))

    def test_msg_out(self):
        st = Stream()
        n = EchoOutputNode()
        n.set_property('msg', 'Hello World')
        st.append_node(n)

        self.assertTrue(st.flow())

    def test_res_out(self):
        st = Stream()
        st.add_resource(FilesystemResource({'src': './*'}))
        st.add_resource(TextResource({'text': 'This is not a list.'}))
        st.append_node(EchoOutputNode({'res': '*'}))

        self.assertTrue(st.flow())

if __name__ == '__main__':
    unittest.main()
