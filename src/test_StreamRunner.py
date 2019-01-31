import unittest
import Stream, StreamRunner
from resources.FilesystemResource import *
from nodes.NullNode import NullNode

class test_StreamRunner(unittest.TestCase):

    def test_run_node(self):
        st = Stream.Stream()
        node = NullNode()
        st_r = StreamRunner.StreamRunner()

        st_r.run(st, node)
        self.assertEqual(st_r._nodeCount, 1)
        

if __name__ == '__main__':
    unittest.main()