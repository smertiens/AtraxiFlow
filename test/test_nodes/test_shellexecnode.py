#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
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
    assert 'HelloWorld' == st.get_resource_by_name('last_shellexec_out').get_data().replace(os.linesep, '')

    # check output
    out = n.get_output()
    assert len(out) == 2
    assert out[0].get_data() == 'HelloWorld' + os.linesep


def test_option_output_command(capsys):
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    n.set_property('echo_command', True)
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    # do not use os.linespe, since the command is output using "print", which ia by default
    # ending the line with a single \n also on windows systems
    assert captured[0].replace('\n', '') == n.get_property('cmd')


def test_option_output(capsys):
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    n.set_property('echo_output', True)
    st.append_node(n)

    assert st.flow()

    captured = capsys.readouterr()
    assert captured[0] == 'HelloWorld\n'
