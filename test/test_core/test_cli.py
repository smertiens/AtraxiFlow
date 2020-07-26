#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.atraxiflow_cli import *
from atraxiflow.base.common import *
from atraxiflow import wayfiles
from click.testing import CliRunner


def test_no_command():
    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert 'Usage: ' in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(version)

    assert result.exit_code == 0
    assert result.output == ax_version + '\n'

def test_server():
    runner = CliRunner()
    #result = runner.invoke(creator)

"""
def test_run(tmp_path):
    tmp_path = str(tmp_path)
    f = os.path.join(tmp_path, 'test.way')

    node1 = EchoOutputNode({'msg': 'Hello'})
    node2 = EchoOutputNode({'msg': 'World'})
    wayfiles.dump(f, [node1, node2])

    runner = CliRunner()
    result = runner.invoke(run, [f])
    assert result.exit_code == 0

    assert 'Hello\nWorld\n' in result.output
"""