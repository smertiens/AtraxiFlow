#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.base.filesystem import *


@pytest.fixture
def make_fixtures(tmpdir_factory):
    path = tmpdir_factory.mktemp('data')
    path.mkdir('folder')

    for n in range(0, 5):
        p = path.join('testfile%s.txt' % n)
        p.write('Hello world')

    return path


def test_move_single_file(make_fixtures, tmpdir):
    dest_dir = str(tmpdir)
    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile0.txt'))]})
    move_node = FSMoveNode({
        'dest': dest_dir
    })

    assert not os.path.exists(dest_dir + '/' + 'testfile0.txt')
    assert os.path.exists(str(make_fixtures.join('testfile0.txt')))

    assert Workflow.create([src, move_node]).run()

    assert os.path.exists(dest_dir + '/' + 'testfile0.txt')
    assert not os.path.exists(str(make_fixtures.join('testfile0.txt')))


def test_move_multiple_files(make_fixtures, tmpdir):
    dest_dir = str(tmpdir)
    paths = []
    n_max = 5

    for n in range(0, n_max):
        p = str(make_fixtures.join('testfile%s.txt' % n))
        paths.append(p)

    src = LoadFilesNode({'paths': paths})
    move_node = FSMoveNode({
        'dest': dest_dir
    })

    for n in range(0, n_max):
        assert not os.path.exists(dest_dir + '/' + 'testfile%s.txt' % n)
        assert os.path.exists(str(make_fixtures.join('testfile%s.txt' % n)))

    assert Workflow.create([src, move_node]).run()

    for n in range(0, n_max):
        assert os.path.exists(dest_dir + '/' + 'testfile%s.txt' % n)
        assert not os.path.exists(str(make_fixtures.join('testfile%s.txt' % n)))


def test_move_single_file_opt_make_dirs(make_fixtures, tmpdir):
    dest_dir = str(tmpdir)
    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile0.txt'))]})
    move_node = FSMoveNode({
        'dest': dest_dir + '/some_folder'
    })

    assert not os.path.exists(dest_dir + '/some_folder')
    assert not os.path.exists(dest_dir + '/' + 'testfile0.txt')
    assert os.path.exists(str(make_fixtures.join('testfile0.txt')))

    assert not Workflow.create([src, move_node]).run()

    # Now with option ON
    move_node = FSMoveNode({
        'dest': dest_dir + '/some_folder',
        'create_dirs': True
    })

    assert not os.path.exists(dest_dir + '/some_folder')
    assert Workflow.create([src, move_node]).run()

    assert os.path.exists(dest_dir + '/some_folder')
    assert os.path.exists(dest_dir + '/' + '/some_folder/testfile0.txt')
    assert not os.path.exists(str(make_fixtures.join('testfile0.txt')))


def test_move_single_file_opt_dry(make_fixtures, tmpdir):
    dest_dir = str(tmpdir)
    src = LoadFilesNode({'paths': [str(make_fixtures.join('testfile0.txt'))]})
    move_node = FSMoveNode({
        'dest': dest_dir,
        'dry': True
    })

    assert not os.path.exists(dest_dir + '/' + 'testfile0.txt')
    assert os.path.exists(str(make_fixtures.join('testfile0.txt')))

    assert Workflow.create([src, move_node]).run()

    assert not os.path.exists(dest_dir + '/' + 'testfile0.txt')
    assert os.path.exists(str(make_fixtures.join('testfile0.txt')))