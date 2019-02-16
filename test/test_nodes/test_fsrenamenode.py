#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
import re
import shutil

from atraxiflow.core.stream import *
from atraxiflow.nodes.filesystem import FSRenameNode, FilesystemResource


def setUp(self):
    logging.getLogger().setLevel(logging.DEBUG)
    os.makedirs(self.get_test_dir())

    for s in ['testfile.txt', 'foo.bar', 'hello']:
        fp = open(os.path.join(self.get_test_dir(), s), 'w')
        fp.write('Hello World')
        fp.close()


def tearDown(self):
    shutil.rmtree(self.get_test_dir())


def test_rename_by_name_prop_single(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = FilesystemResource({'src': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Stream.create().add_resource(res).append_node(node).flow()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))

    assert str(tmpdir.join('testfile_something.txt')) == res.get_data()[0].getAbsolutePath()


def test_rename_by_name_prop_multi(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = FilesystemResource({'src': str(tmpdir.join('*'))})

    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

    assert Stream.create().add_resource(res).append_node(node).flow()
    assert os.path.exists(str(tmpdir.join('testfile_something.txt')))
    assert os.path.exists(str(tmpdir.join('foo_something.bar')))
    assert os.path.exists(str(tmpdir.join('hello_something.')))


def test_rename_by_repl_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = FilesystemResource({'src': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'replace': {
        'testfile': 'foobar',
        re.compile('[\.txt]+$'): '.ext'
    }})

    assert Stream.create().add_resource(res).append_node(node).flow()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == res.get_data()[0].getAbsolutePath()


def test_rename_by_repl_and_name_prop(tmpdir):
    for s in ['testfile.txt', 'foo.bar', 'hello']:
        p = tmpdir.join(s)
        p.write('helloworld')

    res = FilesystemResource({'src': str(tmpdir.join('testfile.txt'))})
    node = FSRenameNode({'replace': {
        'helloworld': 'foobar',
        re.compile('[\.txt]+$'): '.ext'
    },
        'name': '{file.path}/helloworld.txt'
    })

    assert Stream.create().add_resource(res).append_node(node).flow()
    assert os.path.exists(str(tmpdir.join('foobar.ext')))

    assert str(tmpdir.join('foobar.ext')) == res.get_data()[0].getAbsolutePath()
