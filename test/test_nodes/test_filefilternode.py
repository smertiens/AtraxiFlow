#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest
import re
from atraxiflow.core.debug import *
from atraxiflow.nodes.filesystem import FileFilterNode
from atraxiflow.nodes.filesystem import FilesystemResource


@pytest.fixture(scope="module")
def file_fixture(tmpdir_factory):
    testFiles = {
        "file_these_1": 2 * 1024 * 1024,  # M
        "file_are_21_end": 5 * 1024 * 1024,  # M
        "file_four_31_end": 578 * 1024,  # K
        "file_files_4": 10 * 1024,  # K
    }

    path = tmpdir_factory.mktemp('data')

    for name, size in testFiles.items():
        fp = open(str(path.join(name)), "wb")
        fp.seek(size - 1)
        fp.write(b"\0")
        fp.close()

    return path


def test_filter_size_single(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode({"filter": [
        ['file_size', '>', '120K']
    ]})
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    # check output
    assert len(fn.get_output()) == 3


def test_filter_size_multiple(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode('fil')
    fn.set_property("filter", [
        ['file_size', '>', '120K'],
        ['file_size', '<', '4M']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 2


def test_filter_filename_single_contains(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode()
    fn.set_property("filter", [
        ['filename', 'contains', '1']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 3


def test_filter_filename_single_matches(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode()
    fn.set_property("filter", [
        ['filename', 'matches', re.compile(r'file_\w+_\d+_end')]
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 2


def test_filter_filename_single_contains_fail(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode()
    fn.set_property("filter", [
        ['filename', 'contains', 'hellowordl']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 0


def test_filter_filename_single_starts(file_fixture):
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode()
    fn.set_property("filter", [
        ['filename', 'startswith', 'file_these']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 1


def test_filter_filename_single_ends(file_fixture):
    fn = FileFilterNode()
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn.set_property("filter", [
        ['filename', 'endswith', '_end']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 2


def test_filter_filename_multiple(file_fixture):
    fn = FileFilterNode()
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn.set_property("filter", [
        ['filename', 'endswith', '_end'],
        ['filename', 'contains', '21']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 4

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    assert len(fn.get_output()) == 1


def test_filter_filetype(file_fixture):
    file_fixture.mkdir('demo')
    fs = FilesystemResource({'src': str(file_fixture.join('*'))})
    fn = FileFilterNode()
    fn.set_property("filter", [
        ['type', '=', 'file']
    ])
    fn.connect(fs, 'sources')

    assert len(fs.get_data()) == 5

    st = Stream()
    st.add_resource(fs)
    st.append_node(fn)
    assert st.flow()

    # check output
    assert len(fn.get_output()) == 4

    # reset
    fs.set_property('src', str(file_fixture.join('*')))

    fn.set_property("filter", [
        ['type', '=', 'folder']
    ])

    assert st.flow()

    assert len(fn.get_output()) == 1
