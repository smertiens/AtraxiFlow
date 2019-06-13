#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
import pytest
from atraxiflow.base.filesystem import *
from atraxiflow.filesystem import FSObject

@pytest.fixture
def make_fixtures(tmpdir_factory):
    path = tmpdir_factory.mktemp('data')
    path.mkdir('folder')
    p = path.join('testfile.txt')
    p.write('Hello world')

    return path


def test_copy_file_correct(make_fixtures):
    cp = FSCopyNode({'dest': str(make_fixtures.join('folder'))})

    assert not os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))

    src = LoadFilesNode({'path': str(make_fixtures.join('testfile.txt'))})
    assert Workflow.create([src, cp]).run()
    assert os.path.exists(str(make_fixtures.join('folder', 'testfile.txt')))

    # check output
    out = cp.get_output().first()
    assert  isinstance(out, FilesystemResource)
    fso = out.get_value()[0]
    assert isinstance(fso, FSObject)
    assert fso.getAbsolutePath() == str(make_fixtures.join('folder', 'testfile.txt'))


def test_copy_file_dir_not_exists_create(make_fixtures):

    cp = FSCopyNode({
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': True
    })
    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = LoadFilesNode({'path': str(make_fixtures.join('testfile.txt'))})
    assert Workflow.create([src, cp]).run()

    assert os.path.exists(str(make_fixtures.join('folder', 'folder2')))
    assert os.path.exists(str(make_fixtures.join('folder', 'folder2', 'testfile.txt')))


def test_copy_file_dir_not_exists_dont_create(make_fixtures):
    cp = FSCopyNode({
        'dest': str(make_fixtures.join('folder', 'folder2')),
        'create_if_missing': False
    })

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))

    src = LoadFilesNode({'path': str(make_fixtures.join('testfile.txt'))})

    with pytest.raises(FilesystemException):
        assert Workflow.create([src, cp]).run()

    assert not os.path.exists(str(make_fixtures.join('folder', 'folder2')))


def test_copy_dir_correct(make_fixtures):
    dest = str(make_fixtures.join('_temp2'))

    cp = FSCopyNode({
        'dest': dest
    })

    assert not os.path.exists(str(make_fixtures.join("folder", "folder2")))
    assert not os.path.exists(str(os.path.join(dest, "folder")))
    assert not os.path.exists(str(os.path.join(dest, "testfile.txt")))

    src = LoadFilesNode({'path': str(make_fixtures)})
    assert Workflow.create([src, cp]).run()

    assert os.path.exists(str(os.path.join(dest, "folder")))
    assert os.path.exists(str(os.path.join(dest, "testfile.txt")))

    # check output
    out = cp.get_output().first()
    assert isinstance(out, FilesystemResource)
    fso = out.get_value()[0]
    assert isinstance(fso, FSObject)
    assert fso.getAbsolutePath() == dest


def test_copy_dir_dest_exists(make_fixtures):
    dest = make_fixtures.mkdir("_temp2")

    cp = FSCopyNode({
        'dest': str(dest)
    })

    assert os.path.exists(str(dest))

    src = LoadFilesNode({'path': str(make_fixtures)})
    assert not Workflow.create([src, cp]).run()
