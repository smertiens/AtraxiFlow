#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging, os
from common.filesystem import FSObject

class test_FilesystemResource(unittest.TestCase):

    testPath = ""

    def setUp(self):
        logging.disable(logging.FATAL)
        self.testPath = os.path.join(os.getcwd(), "_temp")
        os.makedirs(self.testPath)

        fp = open(os.path.join(self.testPath, "testfile.txt"), "w")
        fp.write("Hello world")
        fp.close()

    def tearDown(self):
        os.unlink(os.path.join(self.testPath, "testfile.txt"))
        os.rmdir(self.testPath)

    def test_basics_folder(self):
        fo = FSObject(self.testPath)
        self.assertTrue(fo.exists())
        self.assertTrue(fo.isFolder())
        self.assertFalse(fo.isFile())

    def test_basics_file(self):
        fo = FSObject(os.path.join(self.testPath, "testfile.txt"))
        self.assertTrue(fo.isFile())
        self.assertFalse(fo.isFolder())
        self.assertFalse(fo.isSymlink())
        self.assertTrue(fo.exists())




if __name__ == '__main__':
    unittest.main()
