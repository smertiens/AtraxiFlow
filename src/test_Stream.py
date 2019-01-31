import unittest
import Stream, StreamRunner
from resources.FilesystemResource import *

class test_Stream(unittest.TestCase):

    def test_stream_add_remove_resource(self):
        st = Stream.Stream()
        res = FilesystemResource('.')
        st.addResource(res)

        self.assertEqual(len(st.getResources()), 1)

        st.removeResource(0)
        self.assertEqual(len(st.getResources()), 0)
        

if __name__ == '__main__':
    unittest.main()