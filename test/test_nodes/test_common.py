#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import builtins
from atraxiflow.base.common import *
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