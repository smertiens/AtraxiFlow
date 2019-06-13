#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os, re

from atraxiflow.core import *
from atraxiflow.filesystem import FSObject
from atraxiflow.base.filesystem import FSRenameNode, LoadFilesNode


def test_rename_by_name_prop_single(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'path': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))

    # check output
    out = node.get_output().first().get_value()[0]
    assert isinstance(out, FSObject)
    assert str(tmpdir.join('testfile_something.txt')) == out.getAbsolutePath()


def test_rename_by_name_prop_multi(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'path': str(tmpdir.join('*'))})
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))
    assert os.path.exists(str(tmpdir.join('foo_something.bar')))
    assert os.path.exists(str(tmpdir.join('hello_something.')))

    # check output
    assert len(node.get_output().items()) == 3
    for out_res in node.get_output().items():
        fso = out_res.get_value()[0]
        assert isinstance(fso, FSObject)


def test_rename_by_repl_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'path': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'replace': {
        'testfile': 'foobar',
        re.compile(r'[\.txt]+$'): '.ext'
    }})

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == node.get_output().first().get_value()[0].getAbsolutePath()


def test_rename_by_repl_and_name_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = LoadFilesNode({'path': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'replace': {
        'helloworld': 'foobar',
        re.compile(r'[\.txt]+$'): '.ext'
    },
        'name': '{file.path}/helloworld.txt'
    })

    assert Workflow.create([res, node]).run()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == node.get_output().first().get_value()[0].getAbsolutePath()
