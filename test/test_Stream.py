import unittest
import Stream, StreamRunner
from resources import TextResource
from resources.FilesystemResource import *

class test_Stream(unittest.TestCase):

    def test_stream_get_resources(self):
        st = Stream.Stream()

        res1 = FilesystemResource("res1_hello")
        st.addResource(res1)
        res2 = FilesystemResource("res2_world")
        st.addResource(res2)
        res3 = FilesystemResource("res3_world")
        st.addResource(res3)

        self.assertEqual(type(st.getResource("FS:*")), list)
        self.assertEqual(3, len(st.getResource("FS:*")))
        self.assertIsInstance(st.getResource("FS:res2_world"), FilesystemResource)
        self.assertEqual(type(st.getResource("FS:*_world")), list)
        self.assertEqual(2, len(st.getResource("FS:*_world")))
        self.assertEqual(3, len(st.getResource("FS:res*")))


    def test_stream_add_remove_resource(self):
         st = Stream.Stream()
         res = FilesystemResource('fs1')
         st.addResource(res)

         self.assertEqual(1, len(st.getResource("FS:*")))

         st.removeResource("FS:fs1")
         self.assertEqual(0, len(st.getResource("FS:*")))

    def test_stream_get_resource_prop(self):
        st = Stream.Stream()
        res = TextResource.TextResource("textres")
        res.setText("demo")
        st.addResource(res)

        self.assertEqual("demo", res.getProperty("text"))
        self.assertEqual("demo", st.getResource("Text:textres.text"))


if __name__ == '__main__':
    unittest.main()