#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import builtins
from atraxiflow.base.common import *
from atraxiflow.base.filesystem import LoadFilesNode
from atraxiflow.core import *


def test_cli_input_create():
    node = CLIInputNode({'prompt': 'Hello'})
    assert 'Hello' == node.property('prompt').value()


def test_cli_input_check_output(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda p: 'Hello World')

    node = CLIInputNode({'prompt': 'Hello'})
    assert Workflow.create([node]).run()

    assert isinstance(node.output, Container)
    out = node.output.find('atraxiflow.TextResource')[0]
    assert out.get_value() == 'Hello World'


def test_echooutput_create():
    n = EchoOutputNode({'msg': 'hello world'})
    assert 'hello world' == n.property('msg').value()


def test_msg_out(capsys):
    n = EchoOutputNode()
    n.property('msg').set_value('Hello World')
    assert Workflow.create([n]).run()

    captured = capsys.readouterr()
    assert captured[0] == 'Hello World\n'

def test_print_resources(capsys):

    Workflow.create([
        LoadFilesNode({'paths': ['./*']}),
        EchoOutputNode({'print_resources': True})
    ]).run()

    captured = capsys.readouterr()
    assert 'input resources found.' in captured[0]


# TODO: reimplement test
"""
def test_execnode_basic(capsys):
    def callback():
        print('Hello callback!')
        return 'done'

    ex = ShellExecNode({'callable': 'callback'})
    assert Workflow.create([ex]).run()
    assert ex.get_output() == 'done'

    captured = capsys.readouterr()
    assert captured[0] == 'Hello callback!\n'
"""