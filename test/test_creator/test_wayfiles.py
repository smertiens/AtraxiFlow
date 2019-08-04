#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os
import pytest

import atraxiflow.creator.wayfiles as wf
from atraxiflow.base.common import *


def test_save_to_file(tmpdir):
    tmpdir = str(tmpdir)
    f = os.path.join(tmpdir, 'demo.way')

    node1 = DelayNode({'time': 5})
    node2 = ShellExecNode({
        'cmd': 'ls -la',
        'echo_cmd': True
    })
    node3 = CLIInputNode({
        'prompt': 'Hello World'
    })

    wf.dump(f, [node1, node2, node3])
    assert os.path.exists(f)

    nodes = wf.load(f)

    assert len(nodes) == 3
    assert isinstance(nodes[0], DelayNode)
    assert nodes[0].property('time').value() == 5
    assert isinstance(nodes[1], ShellExecNode)
    assert nodes[1].property('cmd').value() == 'ls -la'
    assert nodes[1].property('echo_cmd').value() == True
    assert isinstance(nodes[2], CLIInputNode)
    assert nodes[2].property('prompt').value() == 'Hello World'


def test_metadata():
    # Metadata not yet implemented
    pass


def test_raise_on_version_mismatch(tmpdir):
    tmpdir = str(tmpdir)
    f = os.path.join(tmpdir, 'demo.way')

    old_ver = wf.WAYFILE_VERSION
    wf.WAYFILE_VERSION = (wf.WAYFILE_VERSION[0] + 1, 1, 0)
    wf.dump(f, [NullNode()])
    wf.WAYFILE_VERSION = old_ver

    with pytest.raises(wf.WayfileException):
        wf.load(f)