#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest
import Stream
from nodes import TextResource
from nodes.FilesystemResource import *
from nodes.NullNode import NullNode

class test_Stream(unittest.TestCase):

    def test_stream_get_resources(self):
        st = Stream.Stream()

        res1 = FilesystemResource("res1_hello")
        st.add_resource(res1)
        res2 = FilesystemResource("res2_world")
        st.add_resource(res2)
        res3 = FilesystemResource("res3_world")
        st.add_resource(res3)

        self.assertEqual(type(st.get_resources("FS:*")), list)
        self.assertEqual(3, len(st.get_resources("FS:*")))
        self.assertIsInstance(st.get_resources("FS:res2_world"), FilesystemResource)
        self.assertEqual(type(st.get_resources("FS:*_world")), list)
        self.assertEqual(2, len(st.get_resources("FS:*_world")))
        self.assertEqual(3, len(st.get_resources("FS:res*")))

    def test_stream_get_resources_properties(self):
        st = Stream.Stream()

        res1 = FilesystemResource("res1")
        res1.set_property('hello', 'world')
        res1.set_property('lorem', 'ipsum')
        st.add_resource(res1)

        self.assertEqual('world', st.get_resources("FS:res1.hello"))
        self.assertEqual('ipsum', st.get_resources("FS:res1.lorem"))


    def test_stream_add_remove_resource(self):
         st = Stream.Stream()
         res = FilesystemResource('fs1')
         st.add_resource(res)

         self.assertEqual(1, len(st.get_resources("FS:*")))

         st.remove_resource("FS:fs1")
         self.assertEqual(0, len(st.get_resources("FS:*")))

    def test_stream_get_resource_prop(self):
        st = Stream.Stream()
        res = TextResource.TextResource("textres")
        res.set_text("demo")
        st.add_resource(res)

        self.assertEqual("demo", res.get_property("text"))
        self.assertEqual("demo", st.get_resources("Text:textres.text"))


    def test_stream_run_nodes(self):
        st = Stream.Stream()
        st.append_node(NullNode("demo1"))
        st.append_node(NullNode("demo2"))
        st.append_node(NullNode("demo3"))
        st.run()

        self.assertEqual(3, len(st._nodes))



if __name__ == '__main__':
    unittest.main()