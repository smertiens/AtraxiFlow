#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest

from atraxiflow.core import stream
from atraxiflow.core.stream import flow
from atraxiflow.nodes.common import DelayNode, TextResource, EchoOutputNode
from atraxiflow.nodes.common import NullNode
from atraxiflow.nodes.filesystem import *


class test_Stream(unittest.TestCase):

    def test_stream_get_resources(self):
        st = stream.Stream()

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
        st = stream.Stream()

        res1 = FilesystemResource("res1")
        res1.set_property('hello', 'world')
        res1.set_property('lorem', 'ipsum')
        st.add_resource(res1)

        self.assertEqual('world', st.get_resources("FS:res1.hello"))
        self.assertEqual('ipsum', st.get_resources("FS:res1.lorem"))

    def test_stream_add_remove_resource(self):
        st = stream.Stream()
        res = FilesystemResource('fs1')
        st.add_resource(res)

        self.assertEqual(1, len(st.get_resources("FS:*")))

        st.remove_resource("FS:fs1")
        self.assertEqual(0, len(st.get_resources("FS:*")))

    def test_stream_get_resource_prop(self):
        st = stream.Stream()
        res = TextResource("textres")
        res.update_data("demo")
        st.add_resource(res)

        self.assertEqual("demo", res.get_property("text"))
        self.assertEqual("demo", st.get_resources("Text:textres.text"))

    def test_stream_run_nodes(self):
        st = stream.Stream()
        st.append_node(NullNode("demo1"))
        st.append_node(NullNode("demo2"))
        st.append_node(NullNode("demo3"))
        st.flow()

        self.assertEqual(3, len(st._nodes))

    def test_async_branch(self):
        import threading

        st = stream.Stream()
        st.append_node(NullNode())
        st.branch('calculate_1').append_node(DelayNode(props={'time': 1}))
        st.append_node(NullNode())
        st.branch('calculate_2').append_node(DelayNode(props={'time': 1}))
        st.append_node(NullNode())

        self.assertTrue(st.flow())
        self.assertEqual(3, threading.active_count())

    def test_branch_get(self):
        st = stream.Stream()
        st.append_node(NullNode())
        st.branch('demo')

        self.assertEqual(stream.AsyncBranch, type(st.get_branch('demo')))
        self.assertTrue(st.flow())

    def test_branch_stream_inheritance(self):
        st = stream.Stream()
        st.branch('before')
        st.add_resource(TextResource(props={'test': 'Hello World'}))
        st.branch('after')

        self.assertEqual(0, len(st.get_branch('before').get_stream().get_resources('Text:*')))
        self.assertEqual(0, len(st.get_branch('after').get_stream().get_resources('Text:*')))
        self.assertEqual(1, len(st.get_resources('Text:*')))

        self.assertTrue(st.flow())

        self.assertEqual(1, len(st.get_branch('before').get_stream().get_resources('Text:*')))
        self.assertEqual(1, len(st.get_branch('after').get_stream().get_resources('Text:*')))
        self.assertEqual(1, len(st.get_resources('Text:*')))

    def test_operator_overloading(self):
        st = stream.Stream()
        st >> NullNode() >> NullNode() >> NullNode() >> flow()
        self.assertEqual(3, len(st._nodes))

if __name__ == '__main__':
    unittest.main()
