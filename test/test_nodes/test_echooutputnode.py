#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode
from atraxiflow.nodes.filesystem import FilesystemResource
from atraxiflow.nodes.text import TextResource


def test_create_node():
    st = Stream()
    n = EchoOutputNode('demo', {'msg': 'hello world'})

    assert 'hello world' == n.get_property('msg')


def test_msg_out(capsys):
    st = Stream()
    n = EchoOutputNode()
    n.set_property('msg', 'Hello World')
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    assert captured.out == 'Hello World\n'


def test_res_out(capsys):
    st = Stream()
    fsres = FilesystemResource({'src': './*'})
    st.add_resource(fsres)
    st.add_resource(TextResource({'text': 'This is not a list.'}))
    st.append_node(EchoOutputNode({'res': '*'}))

    assert st.flow()

    target = ''
    data = fsres.get_data()
    captured = capsys.readouterr()

    if type(data) in [dict, list, map, tuple]:
        for subdata in data:
            target += str(subdata) + "\n"
    else:
        target += str(data) + "\n"

    target += 'This is not a list.\n'

    assert target == captured.out
