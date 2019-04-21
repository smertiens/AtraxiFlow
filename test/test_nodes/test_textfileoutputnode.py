#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

from atraxiflow.core.stream import *
from atraxiflow.nodes.text import *


def get_file_contents():
    return 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et ' + \
           'dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet ' + \
           'clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'


def test_write_textfile(tmpdir):
    file = str(tmpdir.join('testfile.txt'))
    st = Stream()
    res = TextResource('demo', {'text': get_file_contents()})

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': False
    })
    node.connect(res, 'sources')
    st >> res >> node

    assert st.get_resource_by_name('demo').get_data() == get_file_contents()
    assert st.flow()

    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == get_file_contents()


def test_write_multiple_res(tmpdir):
    file = str(tmpdir.join('testfile_mult.txt'))
    st = Stream()
    res1 = TextResource('part1', {'text': 'Hello'})
    res2 = TextResource('part2', {'text': 'World'})

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': True
    })
    node.connect(res1, 'sources')
    node.connect(res2, 'sources')
    st >> res1 >> res2 >> node

    assert st.flow()
    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == res1.get_data() + '\n' + res2.get_data() + '\n'


def test_write_multiple_res_no_newline(tmpdir):
    file = str(tmpdir.join('testfile_mult.txt'))
    st = Stream()
    res1 = TextResource('part1', {'text': 'Hello'})
    res2 = TextResource('part2', {'text': 'World'})

    node = TextFileOutputNode({
        'filename': file,
        'newline_per_res': False
    })
    node.connect(res1, 'sources')
    node.connect(res2, 'sources')
    st >> res1 >> res2 >> node

    assert st.flow()
    assert os.path.exists(file)

    with open(file, 'r') as f:
        assert f.read() == res1.get_data() + res2.get_data()
