#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os, re

from atraxiflow.core import *
from atraxiflow.base.filesystem import FSRenameNode, LoadFilesNode
from atraxiflow.base.resources import FilesystemResource

def test_rename_by_name_prop_single(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'paths': [str(tmpdir.join('testfile.txt'))]})
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))

    # check output
    out = node.get_output().first()
    assert isinstance(out, FilesystemResource)
    assert str(tmpdir.join('testfile_something.txt')) == out.get_absolute_path()


def test_rename_by_name_prop_multi(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'paths': [str(tmpdir.join('*'))]})
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))
    assert os.path.exists(str(tmpdir.join('foo_something.bar')))
    assert os.path.exists(str(tmpdir.join('hello_something.')))

    # check output
    assert node.get_output().size()== 3
    for out_res in node.get_output().items():
        assert isinstance(out_res, FilesystemResource)


def test_rename_by_repl_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'paths': [str(tmpdir.join('testfile.txt'))]})
    node = FSRenameNode({'replace': {
        'testfile': 'foobar',
        re.compile(r'[\.txt]+$'): '.ext'
    }})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == node.get_output().first().get_absolute_path()


def test_rename_by_repl_and_name_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'paths': [str(tmpdir.join('testfile.txt'))]})
    node = FSRenameNode({'replace': {
        'helloworld': 'foobar',
        re.compile(r'[\.txt]+$'): '.ext'
    },
        'name': '{file.path}/helloworld.txt'
    })

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == node.get_output().first().get_absolute_path()
