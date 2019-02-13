#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import os
import unittest

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.filesystem import FilesystemResource, FSCopyNode


class test_FSCopyNode(unittest.TestCase):
    testPath = ""

    def get_test_stream(self):
        st = Stream()

        return st

    def setUp(self):
        logging.disable(logging.FATAL)
        self.testPath = os.path.join(os.getcwd(), "_temp")
        os.makedirs(os.path.join(self.testPath, "folder"))

        fp = open(os.path.join(self.testPath, "testfile.txt"), "w")
        fp.write("Hello world")
        fp.close()

    def tearDown(self):

        if os.path.exists(os.path.join(self.testPath, "folder", "testfile.txt")):
            os.unlink(os.path.join(self.testPath, "folder", "testfile.txt"))
        if os.path.exists(os.path.join(self.testPath, "folder", "folder2", "testfile.txt")):
            os.unlink(os.path.join(self.testPath, "folder", "folder2", "testfile.txt"))
        if os.path.exists(os.path.join(self.testPath, "folder", "folder2")):
            os.rmdir(os.path.join(self.testPath, "folder", "folder2"))

        if os.path.exists(os.path.join(os.getcwd(), "_temp2", "testfile.txt")):
            os.unlink(os.path.join(os.getcwd(), "_temp2", "testfile.txt"))

        if os.path.exists(os.path.join(os.getcwd(), "_temp2", "folder")):
            os.rmdir(os.path.join(os.getcwd(), "_temp2", "folder"))
        if os.path.exists(os.path.join(os.getcwd(), "_temp2")):
            os.rmdir(os.path.join(os.getcwd(), "_temp2"))

        os.unlink(os.path.join(self.testPath, "testfile.txt"))
        os.rmdir(os.path.join(self.testPath, "folder"))
        os.rmdir(self.testPath)

    def test_copy_file_correct(self):
        st = self.get_test_stream()
        cp = FSCopyNode("cp", {'dest': os.path.join(self.testPath, "folder")})

        self.assertFalse(os.path.exists(os.path.join(self.testPath, "folder", "testfile.txt")))

        src = FilesystemResource("srcres")
        src.set_property('sourcePattern', os.path.join(self.testPath, "testfile.txt"))
        st.add_resource(src)
        st.append_node(cp)
        self.assertTrue(st.run())

        self.assertTrue(os.path.exists(os.path.join(self.testPath, "folder", "testfile.txt")))

    def test_copy_file_dir_not_exists_create(self):
        st = self.get_test_stream()
        cp = FSCopyNode("cp", {
            'dest': os.path.join(self.testPath, "folder", "folder2"),
            'create_if_missing': True
        })

        self.assertFalse(os.path.exists(os.path.join(self.testPath, "folder", "folder2")))

        src = FilesystemResource("srcres")
        src.set_property('sourcePattern', os.path.join(self.testPath, "testfile.txt"))
        st.add_resource(src)
        st.append_node(cp)
        self.assertTrue(st.run())

        self.assertTrue(os.path.exists(os.path.join(self.testPath, "folder", "folder2")))
        self.assertTrue(os.path.exists(os.path.join(self.testPath, "folder", "folder2", "testfile.txt")))

    def test_copy_file_dir_not_exists_dont_create(self):
        st = self.get_test_stream()
        cp = FSCopyNode("cp", {
            'dest': os.path.join(self.testPath, "folder", "folder2"),
            'create_if_missing': False
        })

        self.assertFalse(os.path.exists(os.path.join(self.testPath, "folder", "folder2")))

        src = FilesystemResource("srcres")
        src.set_property('sourcePattern', os.path.join(self.testPath, "testfile.txt"))
        st.add_resource(src)
        st.append_node(cp)
        self.assertFalse(st.run())

        self.assertFalse(os.path.exists(os.path.join(self.testPath, "folder", "folder2")))

    def test_copy_dir_correct(self):
        dest = os.path.join(os.getcwd(), "_temp2");
        st = self.get_test_stream()
        cp = FSCopyNode("cp", {
            'dest': dest
        })

        self.assertFalse(os.path.exists(os.path.join(self.testPath, "folder", "folder2")))
        self.assertFalse(os.path.exists(os.path.join(dest, "folder")))
        self.assertFalse(os.path.exists(os.path.join(dest, "testfile.txt")))

        src = FilesystemResource("srcres")
        src.set_property('sourcePattern', self.testPath)
        st.add_resource(src)
        st.append_node(cp)
        self.assertTrue(st.run())

        self.assertTrue(os.path.exists(os.path.join(dest, "folder")))
        self.assertTrue(os.path.exists(os.path.join(dest, "testfile.txt")))

    def test_copy_dir_dest_exists(self):
        dest = os.path.join(os.getcwd(), "_temp2");
        st = self.get_test_stream()
        cp = FSCopyNode("cp", {
            'dest': dest
        })

        os.makedirs(dest)
        self.assertTrue(os.path.exists(dest))

        src = FilesystemResource("srcres")
        src.set_property('sourcePattern', self.testPath)
        st.add_resource(src)
        st.append_node(cp)
        self.assertFalse(st.run())


if __name__ == '__main__':
    unittest.main()
