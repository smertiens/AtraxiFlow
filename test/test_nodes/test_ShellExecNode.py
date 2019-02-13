#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging
from atraxiflow.Stream import Stream
from atraxiflow.nodes.ShellExecNode import ShellExecNode
from atraxiflow.nodes.EchoOutputNode import EchoOutputNode

class test_ShellExecNode(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def tearDown(self):
        #if os.path.exists(os.path.join(os.getcwd(), 'test.txt')):
        #    os.unlink(os.path.join(os.getcwd(), 'test.txt'))
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
        self.assertTrue(st.run())

        self.assertTrue(n.get_property('cmd'), st.get_resource_by_name('last_shellexec_out').get_data().replace('\n', ''))


if __name__ == '__main__':
    unittest.main()