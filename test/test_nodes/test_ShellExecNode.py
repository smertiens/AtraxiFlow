#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging, os
from Stream import Stream
from nodes.ShellExecNode import ShellExecNode

class test_ShellExecNode(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def tearDown(self):
        if os.path.exists(os.path.join(os.getcwd(), 'test.txt')):
            os.unlink(os.path.join(os.getcwd(), 'test.txt'))

    def test_create_node(self):
        st = Stream()
        n = ShellExecNode()
        n.set_property('cmd', 'ls')

        self.assertEqual('ls', n.get_property('cmd'))

    def test_run_command(self):
        st = Stream()
        n = ShellExecNode()
        n.set_property('cmd', 'echo "Hello World" > ' + os.path.join(os.getcwd(), 'test.txt'))
        st.append_node(n)

        self.assertTrue(st.run())
        fp = open(os.path.join(os.getcwd(), 'test.txt'), 'r')
        self.assertEqual("Hello World\n", fp.read())
        fp.close()



if __name__ == '__main__':
    unittest.main()