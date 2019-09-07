#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

from atraxiflow.core import *
from atraxiflow.base.text import *
from atraxiflow.base.common import NullNode

def get_file_contents():
    return 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et ' + \
           'dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet ' + \
           'clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'


def test_write_textfile(tmpdir):
    file = str(tmpdir.join('testfile.txt'))

    out_node = NullNode()
    out_node.output.add(TextResource(get_file_contents()))

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': False
    })
    assert Workflow.create([out_node, node]).run()
    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == get_file_contents()


def test_write_multiple_res(tmpdir):
    file = str(tmpdir.join('testfile_mult.txt'))

    out_node = NullNode()
    out_node.output.add(TextResource('Hello'))
    out_node.output.add(TextResource('World'))

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': True
    })

    assert Workflow.create([out_node, node]).run()
    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == 'Hello\nWorld\n'


def test_write_multiple_res_no_newline(tmpdir):
    file = str(tmpdir.join('testfile_mult.txt'))

    out_node = NullNode()
    out_node.output.add(TextResource('Hello'))
    out_node.output.add(TextResource('World'))

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': False
    })

    assert Workflow.create([out_node, node]).run()
    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == 'HelloWorld'
