#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, os, logging, shutil, re
from atraxiflow.core.stream import *
from atraxiflow.nodes.filesystem import FSRenameNode, FilesystemResource

class test_FSRenameNode(unittest.TestCase):

    def get_test_dir(self):
        return os.path.realpath(os.path.join('.', '_temp'))

    def setUp(self):
        logging.getLogger().setLevel(logging.DEBUG)
        os.makedirs(self.get_test_dir())

        for s in ['testfile.txt', 'foo.bar', 'hello']:
            fp = open(os.path.join(self.get_test_dir(), s) , 'w')
            fp.write('Hello World')
            fp.close()

    def tearDown(self):
        shutil.rmtree(self.get_test_dir())

    def test_rename_by_name_prop_single(self):
        res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), 'testfile.txt'))})
        node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

        self.assertTrue(Stream.create().add_resource(res).append_node(node).flow())
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'testfile_something.txt')))

        self.assertEqual(os.path.join(self.get_test_dir(), 'testfile_something.txt'), res.get_data()[0].getAbsolutePath())

    def test_rename_by_name_prop_multi(self):
        res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), '*'))})

        node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})

        self.assertTrue(Stream.create().add_resource(res).append_node(node).flow())
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'testfile_something.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'foo_something.bar')))
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'hello_something.')))

    def test_rename_by_repl_prop(self):
        res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), 'testfile.txt'))})
        node = FSRenameNode({'replace': {
            'testfile' : 'foobar',
            re.compile('[\.txt]+$') : '.ext'
        }})

        self.assertTrue(Stream.create().add_resource(res).append_node(node).flow())
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'foobar.ext')))

        self.assertEqual(os.path.join(self.get_test_dir(), 'foobar.ext'), res.get_data()[0].getAbsolutePath())

    def test_rename_by_repl_and_name_prop(self):
        res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), 'testfile.txt'))})
        node = FSRenameNode({'replace': {
            'helloworld' : 'foobar',
            re.compile('[\.txt]+$') : '.ext'
        },
            'name': '{file.path}/helloworld.txt'
        })

        self.assertTrue(Stream.create().add_resource(res).append_node(node).flow())
        self.assertTrue(os.path.exists(os.path.join(self.get_test_dir(), 'foobar.ext')))

        self.assertEqual(os.path.join(self.get_test_dir(), 'foobar.ext'), res.get_data()[0].getAbsolutePath())
