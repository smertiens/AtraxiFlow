#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.filesystem import FSObject


def test_basics_folder(tmpdir):
    fo = FSObject(tmpdir)
    assert fo.exists()
    assert fo.isFolder()
    assert not fo.isFile()


def test_basics_file(tmpdir):
    p = tmpdir.join('testfile.txt')
    p.write('content', 'w')
    fo = FSObject(str(p))

    assert fo.isFile()
    assert not fo.isFolder()
    assert not fo.isSymlink()
    assert fo.exists()
