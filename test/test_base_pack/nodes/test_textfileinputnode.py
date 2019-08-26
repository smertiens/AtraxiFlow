#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.base.text import *
from atraxiflow.core import *

def get_file_contents():
    return 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et ' + \
        'dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet ' + \
        'clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'

@pytest.fixture
def create_testfile(tmpdir_factory):
    path = tmpdir_factory.mktemp('data')
    path.mkdir('folder')
    p = path.join('testfile.txt')
    p.write(get_file_contents())

    return str(p)


def test_read_textfile(create_testfile):
    file = create_testfile

    node = TextFileInputNode({
        'filename': file
    })

    assert Workflow.create([node]).run()
    assert node.get_output().first().get_value() == get_file_contents()
