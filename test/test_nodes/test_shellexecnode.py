#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
from atraxiflow.core import *
from atraxiflow.base.common import ShellExecNode, EchoOutputNode


def test_create_node():
    n = ShellExecNode({'cmd': 'ls'})
    assert 'ls' == n.property('cmd').value()


def test_run_command():
    n = ShellExecNode({'cmd': 'echo HelloWorld'})
    assert Workflow.create([n]).run()
    assert 'HelloWorld' == n.get_output().first().get_value().replace(os.linesep, '')

    # check output
    out = n.get_output().items()
    assert len(out) == 2
    assert out[0].get_value() == 'HelloWorld' + os.linesep


def test_option_output_command(capsys):

    n = ShellExecNode({
        'cmd': 'echo HelloWorld',
        'echo_cmd':True
    })

    assert Workflow.create([n]).run()

    captured = capsys.readouterr()
    # do not use os.linespe, since the command is output using "print", which ia by default
    # ending the line with a single \n also on windows systems
    assert captured[0].replace('\n', '') == n.property('cmd').value()


def test_option_output(capsys):
    n = ShellExecNode({
        'cmd': 'echo HelloWorld',
        'echo_output': True
    })

    assert Workflow.create([n]).run()

    captured = capsys.readouterr()
    assert captured[0] == 'HelloWorld\n'
