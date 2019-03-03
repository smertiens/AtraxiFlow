#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.core import stream
from atraxiflow.core.stream import flow
from atraxiflow.nodes.common import DelayNode, TextResource
from atraxiflow.nodes.common import NullNode
from atraxiflow.nodes.filesystem import *


def test_stream_get_resources():
    st = stream.Stream()

    res1 = FilesystemResource("res1_hello")
    st.add_resource(res1)
    res2 = FilesystemResource("res2_world")
    st.add_resource(res2)
    res3 = FilesystemResource("res3_world")
    st.add_resource(res3)

    assert type(st.get_resources("FS:*")) == list
    assert 3 == len(st.get_resources("FS:*"))
    assert isinstance(st.get_resources("FS:res2_world")[0], FilesystemResource)
    assert type(st.get_resources("FS:*_world")) == list
    assert 2 == len(st.get_resources("FS:*_world"))
    assert 3 == len(st.get_resources("FS:res*"))

    st.add_resource(TextResource())
    st.add_resource(TextResource())

    # print(st.get_resources('*'))
    assert 5 == len(st.get_resources('*'))


def test_stream_get_resources_properties():
    st = stream.Stream()

    res1 = FilesystemResource("res1")
    res1.set_property('hello', 'world')
    res1.set_property('lorem', 'ipsum')
    st.add_resource(res1)

    assert 'world' == st.get_resources("FS:res1.hello")
    assert 'ipsum' == st.get_resources("FS:res1.lorem")


def test_stream_add_remove_resource():
    st = stream.Stream()
    res = FilesystemResource('fs1')
    st.add_resource(res)

    assert 1 == len(st.get_resources("FS:*"))

    st.remove_resource("FS:fs1")
    assert 0 == len(st.get_resources("FS:*"))


def test_stream_get_resource_prop():
    st = stream.Stream()
    res = TextResource("textres")
    res.update_data("demo")
    st.add_resource(res)

    assert "demo" == res.get_property("text")
    assert "demo" == st.get_resources("Text:textres.text")


def test_stream_run_nodes():
    st = stream.Stream()
    st.append_node(NullNode("demo1"))
    st.append_node(NullNode("demo2"))
    st.append_node(NullNode("demo3"))
    st.flow()

    assert 3 == len(st._nodes)


def test_async_branch():
    import threading

    st = stream.Stream()
    st.append_node(NullNode())
    st.branch('calculate_1').append_node(DelayNode(props={'time': 1}))
    st.append_node(NullNode())
    st.branch('calculate_2').append_node(DelayNode(props={'time': 1}))
    st.append_node(NullNode())

    assert st.flow()
    assert 3 == threading.active_count()


def test_branch_get():
    st = stream.Stream()
    st.append_node(NullNode())
    st.branch('demo')

    assert stream.AsyncBranch == type(st.get_branch('demo'))
    assert st.flow()


def test_branch_stream_inheritance():
    st = stream.Stream()
    st.branch('before')
    st.add_resource(TextResource(props={'test': 'Hello World'}))
    st.branch('after')

    assert 0 == len(st.get_branch('before').get_stream().get_resources('Text:*'))
    assert 0 == len(st.get_branch('after').get_stream().get_resources('Text:*'))
    assert 1 == len(st.get_resources('Text:*'))

    assert st.flow()

    assert 1 == len(st.get_branch('before').get_stream().get_resources('Text:*'))
    assert 1 == len(st.get_branch('after').get_stream().get_resources('Text:*'))
    assert 1 == len(st.get_resources('Text:*'))


def test_operator_overloading():
    st = stream.Stream()
    st >> NullNode() >> NullNode() >> NullNode() >> flow()
    assert 3 == len(st._nodes)


def test_fail_on_illegal_resource_prefix():
    class TestRes(Resource):
        def __init__(self, name="", props=None):
            self.name = name
            self._known_properties = {}
            self._stream = None
            self._listeners = {}

            self.name, self.properties = self.get_properties_from_args(name, props)

        def get_prefix(self):
            return 'AX'

        def remove_data(self, obj):
            # remove data
            pass

        def update_data(self, data):
            pass

        def get_data(self, key=""):
            self.check_properties()

            # get data
            return self.get_property(key)

    st = stream.Stream()

    with pytest.raises(ResourceException):
        st.add_resource(TestRes())

    st.add_resource(TextResource())


def test_fail_on_illegal_stream_pos():
    st = stream.Stream()
    st.append_node(FSCopyNode({'sources': 'AX:prev.output', 'dest': '.'}))

    with pytest.raises(ExecutionException):
        st.flow()


def test_fail_on_illegal_ax_query():
    st = stream.Stream()
    st.append_node(FSCopyNode({'sources': 'AX:something_else', 'dest': '.'}))

    with pytest.raises(ResourceException):
        st.flow()


def test_get_node_by_name():
    st = stream.Stream()
    node = NullNode('demo_node')
    st.append_node(node)

    assert st.get_node_by_name('demo_node') == node


# TODO test
def test_get_node_output_from_prev():
    pass


# TODO test
def test_get_node_output_by_name():
    pass
