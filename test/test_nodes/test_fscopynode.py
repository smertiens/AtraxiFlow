#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

import pytest

from atraxiflow.core.exceptions import *
from atraxiflow.core.stream import Stream
from atraxiflow.nodes.filesystem import FilesystemResource, FSCopyNode


def get_test_stream():
    st = Stream()

    return st


@pytest.fixture
def make_fixtures(tmpdir_factory):
    path = tmpdir_factory.mktemp('data')
    path.mkdir('folder')
    p = path.join('testfile.txt')
    p.write('Hello world')

    return path


def test_copy_file_correct(make_fixtures):
    st = get_test_stream()
    cp = FSCopyNode("cp", {'dest': str(make_fixtures.join('folder'))})

    assert not os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))

    src = FilesystemResource("srcres")
    src.set_property('src', str(make_fixtures.join('testfile.txt')))
    st.add_resource(src)
    st.append_node(cp)
    assert st.flow()

    assert os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))


def test_copy_file_dir_not_exists_create(make_fixtures):
    st = get_test_stream()
    cp = FSCopyNode("cp", {
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': True
    })

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = FilesystemResource("srcres")
    src.set_property('src', str(make_fixtures.join('testfile.txt')))
    st.add_resource(src)
    st.append_node(cp)
    assert st.flow()

    assert os.path.exists(str(make_fixtures.join('folder', 'folder2')))
    assert os.path.exists(str(make_fixtures.join('folder', 'folder2', 'testfile.txt')))


def test_copy_file_dir_not_exists_dont_create(make_fixtures):
    st = get_test_stream()
    cp = FSCopyNode("cp", {
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': False
    })

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = FilesystemResource("srcres")
    src.set_property('src', str(make_fixtures.join('testfile.txt')))
    st.add_resource(src)
    st.append_node(cp)

    with pytest.raises(FilesystemException):
        assert not st.flow()

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))


def test_copy_dir_correct(make_fixtures):
    dest = str(make_fixtures.join('_temp2'))

    st = get_test_stream()
    cp = FSCopyNode("cp", {
        'dest': dest
    })

    assert not os.path.exists(make_fixtures.join("folder", "folder2"))
    assert not os.path.exists(os.path.join(dest, "folder"))
    assert not os.path.exists(os.path.join(dest, "testfile.txt"))

    src = FilesystemResource("srcres")
    src.set_property('src', str(make_fixtures))
    st.add_resource(src)
    st.append_node(cp)
    assert st.flow()

    assert os.path.exists(os.path.join(dest, "folder"))
    assert os.path.exists(os.path.join(dest, "testfile.txt"))


def test_copy_dir_dest_exists(make_fixtures):
    dest = make_fixtures.mkdir("_temp2")

    st = get_test_stream()
    cp = FSCopyNode("cp", {
        'dest': str(dest)
    })

    assert os.path.exists(dest)

    src = FilesystemResource("srcres")
    src.set_property('src', str(make_fixtures))
    st.add_resource(src)
    st.append_node(cp)
    assert not st.flow()
