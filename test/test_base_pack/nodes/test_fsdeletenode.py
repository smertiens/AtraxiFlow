#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.base.filesystem import *


def test_delete_files(tmpdir):
    f1 = tmpdir.join('file1')
    f2 = tmpdir.join('file2')
    f1.write('')
    f2.write('')

    assert os.path.exists(str(tmpdir.join('file1')))
    assert os.path.exists(str(tmpdir.join('file2')))

    get_files = LoadFilesNode({'paths': [str(tmpdir) + '/file*']})
    del_node = FSDeleteNode()

    assert Workflow.create([get_files, del_node]).run()

    assert not os.path.exists(str(tmpdir.join('file1')))
    assert not os.path.exists(str(tmpdir.join('file2')))


def test_delete_files_dry(tmpdir):
    f1 = tmpdir.join('file1')
    f1.write('')

    assert os.path.exists(str(tmpdir.join('file1')))

    get_files = LoadFilesNode({'paths': [str(tmpdir) + '/file1']})
    del_node = FSDeleteNode({'dry': True})

    assert Workflow.create([get_files, del_node]).run()
    assert os.path.exists(str(tmpdir.join('file1')))


def test_delete_directories(tmpdir):
    empty_dir = tmpdir.mkdir('empty')
    nonempty_dir = tmpdir.mkdir('nonempty')
    f1 = nonempty_dir.join('file1')
    f1.write('')

    assert os.path.exists(str(tmpdir.join('empty')))
    assert os.path.exists(str(tmpdir.join('nonempty', 'file1')))

    # delete empty folder
    get_files = LoadFilesNode({'paths': [str(empty_dir)]})
    del_node = FSDeleteNode()

    assert Workflow.create([get_files, del_node]).run()
    assert not os.path.exists(str(tmpdir.join('empty')))

    # try to delete non-empty folder
    get_files = LoadFilesNode({'paths': [str(nonempty_dir)]})
    del_node = FSDeleteNode()

    assert Workflow.create([get_files, del_node]).run()
    assert os.path.exists(str(tmpdir.join('nonempty')))

    del_node = FSDeleteNode({'del_nonempty_dirs': True})
    assert Workflow.create([get_files, del_node]).run()
    assert not os.path.exists(str(tmpdir.join('nonempty')))


def test_delete_symlink(tmpdir):
    f1 = tmpdir.join('file1')
    f1.write('')
    assert os.path.exists(str(tmpdir.join('file1')))

    os.symlink(str(f1), tmpdir.join('f1.link'))

    assert os.path.exists(str(tmpdir.join('f1.link')))
    assert os.path.islink(str(tmpdir.join('f1.link')))

    # try to delete symlink
    get_files = LoadFilesNode({'paths': [str(tmpdir.join('f1.link'))]})
    del_node = FSDeleteNode()

    assert Workflow.create([get_files, del_node]).run()
    assert not os.path.exists(str(tmpdir.join('f1.link')))
    assert not os.path.exists(str(tmpdir.join('file1')))