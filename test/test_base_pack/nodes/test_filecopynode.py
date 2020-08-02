#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
import pytest
from atraxiflow.base.filesystem import *

@pytest.fixture
def make_fixtures(tmpdir_factory):
    # tmpdir_factory: session-scoped fixture
    
    path = tmpdir_factory.mktemp('data')
    path.mkdir('folder')
    p = path.join('testfile.txt')
    p.write('Hello world')

    return path


def test_copy_file_correct(make_fixtures):
    cp = FSCopyNode({'dest': str(make_fixtures.join('folder'))})

    assert not os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))

    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile.txt'))]})
    assert Workflow.create([src, cp]).run()
    assert os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))

    # check output
    out = cp.get_output().first()
    assert isinstance(out, FilesystemResource)
    assert out.get_absolute_path() == str(make_fixtures.join('folder', 'testfile.txt'))


def test_copy_file_dir_not_exists_create(make_fixtures):

    cp = FSCopyNode({
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': True
    })
    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile.txt'))]})
    assert Workflow.create([src, cp]).run()

    assert os.path.exists(str(make_fixtures.join('folder', 'folder2')))
    assert os.path.exists(str(make_fixtures.join('folder', 'folder2', 'testfile.txt')))


def test_copy_file_dir_not_exists_dont_create(make_fixtures, caplog):
    cp = FSCopyNode({
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': False
    })

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile.txt'))]})

    assert not Workflow.create([src, cp]).run()
    assert 'Destination does not exist and create_if_missing is False' in caplog.text
    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))


def test_copy_dir_correct(make_fixtures):
    dest = str(make_fixtures.join('_temp2'))

    cp = FSCopyNode({
        'dest': dest
    })

    assert not os.path.exists(str(make_fixtures.join("folder", "folder2")))
    assert not os.path.exists(str(os.path.join(dest, "folder")))
    assert not os.path.exists(str(os.path.join(dest, "testfile.txt")))

    src = LoadFilesNode({'paths': [str(make_fixtures)]})
    assert Workflow.create([src, cp]).run()

    assert os.path.exists(str(os.path.join(dest, "folder")))
    assert os.path.exists(str(os.path.join(dest, "testfile.txt")))

    # check output
    out = cp.get_output().first()
    assert isinstance(out, FilesystemResource)
    assert out.get_absolute_path() == dest


def test_copy_dir_dest_exists(make_fixtures):
    dest = make_fixtures.mkdir("_temp2")

    cp = FSCopyNode({
        'dest': str(dest)
    })

    assert os.path.exists(str(dest))

    src = LoadFilesNode({'paths': [str(make_fixtures)]})
    assert not Workflow.create([src, cp]).run()
