#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest, logging, os
from atraxiflow.nodes.FilesystemResource import FilesystemResource
from atraxiflow.common.filesystem import FSObject

class test_FilesystemResource(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)
        self.testPath = os.path.join(os.getcwd(), "_temp")
        os.makedirs(os.path.join(self.testPath, "folder"))

        fp = open(os.path.join(self.testPath, "testfile.txt"), "w")
        fp.write("Hello world")
        fp.close()

    def tearDown(self):
        os.unlink(os.path.join(self.testPath, "testfile.txt"))
        os.rmdir(os.path.join(self.testPath, "folder"))
        os.rmdir(self.testPath)

    def test_resolve_wildcards(self):
        fs = FilesystemResource()
        fs.set_property("sourcePattern", os.path.join(self.testPath, "*"))
        data = fs.get_data()

        self.assertTrue(fs._resolved)
        self.assertEqual(2, len(data))
        self.assertIsInstance(data[0], FSObject)
        self.assertIsInstance(data[1], FSObject)

    def test_resolve_no_wildcards(self):
        fs = FilesystemResource()
        fs.set_property("sourcePattern", self.testPath)
        data = fs.get_data()

        self.assertTrue(fs._resolved)
        self.assertEqual(1, len(data))
        self.assertIsInstance(data[0], FSObject)

if __name__ == '__main__':
    unittest.main()
