#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import unittest

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import ShellExecNode, EchoOutputNode


class test_ShellExecNode(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def tearDown(self):
        pass

    def test_create_node(self):
        st = Stream()
        n = ShellExecNode()
        n.set_property('cmd', 'ls')

        self.assertEqual('ls', n.get_property('cmd'))

    def test_run_command(self):
        st = Stream()
        n = ShellExecNode()
        n.set_property('cmd', 'echo HelloWorld')
        st.append_node(n)
        st.append_node(EchoOutputNode(props={'msg': '{Res::last_shellexec_out}'}))
        self.assertTrue(st.flow())

        self.assertTrue(n.get_property('cmd'),
                        st.get_resource_by_name('last_shellexec_out').get_data().replace('\n', ''))


if __name__ == '__main__':
    unittest.main()
