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

    assert 'ls'== n.get_property('cmd')

#todo refactor to capture output
def test_run_command():
    st = Stream()
    n = ShellExecNode()
    n.set_property('cmd', 'echo HelloWorld')
    st.append_node(n)
    st.append_node(EchoOutputNode(props={'msg': '{Res::last_shellexec_out}'}))
    assert st.flow()

    assert 'HelloWorld' == st.get_resource_by_name('last_shellexec_out').get_data().replace('\n', '')
