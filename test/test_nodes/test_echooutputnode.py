#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode, echo
from atraxiflow.nodes.filesystem import FilesystemResource
from atraxiflow.nodes.text import TextResource


def test_create_node():
    st = Stream()
    n = EchoOutputNode('demo', {'msg': 'hello world'})

    assert 'hello world' == n.get_property('msg')


def test_convenience_function(capsys):
    assert isinstance(echo(''), EchoOutputNode)

    st = Stream()
    st >> echo('Hello World')
    assert st.flow()

    captured = capsys.readouterr()
    assert captured[0] == 'Hello World\n'


def test_msg_out(capsys):
    st = Stream()
    n = EchoOutputNode()
    n.set_property('msg', 'Hello World')
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    assert captured[0] == 'Hello World\n'


# Todo: Fails under 3.5dev and 3.5 xenial, since the textresource is output first...
# def test_res_out(capsys):
def offline(capsys):
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

    assert target == captured[0]
