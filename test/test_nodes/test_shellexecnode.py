#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import ShellExecNode, EchoOutputNode


def test_create_node():
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'ls')

    assert 'ls' == n.get_property('cmd')


def test_run_command():
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    st.append_node(n)
    st.append_node(EchoOutputNode(props={'msg': '{Res::last_shellexec_out}'}))
    assert st.flow()
    assert 'HelloWorld' == st.get_resource_by_name('last_shellexec_out').get_data().replace('\n', '')

    # check output
    out = n.get_output()
    assert len(out) == 2
    assert out[0].get_data() == 'HelloWorld\n'


def test_option_output_command(capsys):
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    n.set_property('echo_command', True)
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    assert captured[0] == n.get_property('cmd') + '\n'


def test_option_output(capsys):
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    n.set_property('echo_output', True)
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    assert captured[0] == 'HelloWorld\n\n'
