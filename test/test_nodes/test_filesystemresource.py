#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.filesystem import FSObject
from atraxiflow.nodes.filesystem import FilesystemResource


def test_resolve_wildcards(tmpdir):
    tmpdir.mkdir('test')
    p = tmpdir.join('testfile')
    p.write('hlloworld')

    fs = FilesystemResource()
    fs.set_property("src", str(tmpdir.join("*")))
    data = fs.get_data()

    assert fs._resolved
    assert len(data) == 2
    assert isinstance(data[0], FSObject)
    assert isinstance(data[1], FSObject)


def test_resolve_no_wildcards(tmpdir):
    fs = FilesystemResource()
    fs.set_property("src", str(tmpdir))
    data = fs.get_data()

    assert fs._resolved
    assert len(data) == 1
    assert isinstance(data[0], FSObject)
