#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.nodes.text import *
from atraxiflow.core.stream import *

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

    st = Stream()
    node = TextFileInputNode({
        'filename': file,
        'resource_name': 'file_content'
    })
    st >> node

    assert st.flow()
    assert st.get_resource_by_name('file_content').get_data() == get_file_contents()
    assert node.get_output().get_data() == get_file_contents()
