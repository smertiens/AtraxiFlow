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
from atraxiflow.nodes.filesystem import FileFilterNode
from atraxiflow.nodes.filesystem import FilesystemResource


class test_FileFilterNode(unittest.TestCase):
    testPath = ""
    testFiles = {
        "file1": 2 * 1024 * 1024,  # M
        "file2": 5 * 1024 * 1024,  # M
        "file3": 578 * 1024,  # K
        "file4": 10 * 1024,  # K
    }

    def setUp(self):
        logging.disable(logging.FATAL)
        self.testPath = os.path.realpath(os.path.join(os.getcwd(), "_testfiles"))
        os.makedirs(self.testPath)

        for name, size in self.testFiles.items():
            fp = open(os.path.join(self.testPath, name), "wb")
            fp.seek(size - 1)
            fp.write(b"\0")
            fp.close()

    def tearDown(self):
        for name, size in self.testFiles.items():
            os.unlink(os.path.join(self.testPath, name))
        os.rmdir(self.testPath)

    def test_filter_size_single(self):
        fn = FileFilterNode()
        fn.set_property("filter", [
            ['file_size', '>', '120K']
        ])

        fs = FilesystemResource({'src': os.path.join(self.testPath, "*")})
        self.assertEqual(4, len(fs.get_data()))

        st = Stream()
        st.add_resource(fs)
        st.append_node(fn)
        st.flow()

        self.assertEqual(3, len(fs.get_data()))

    def test_filter_size_multiple(self):
        fn = FileFilterNode()
        fn.set_property("filter", [
            ['file_size', '>', '120K'],
            ['file_size', '<', '4M']
        ])

        fs = FilesystemResource({'src': os.path.join(self.testPath, "*")})
        self.assertEqual(4, len(fs.get_data()))

        st = Stream()
        st.add_resource(fs)
        st.append_node(fn)
        self.assertTrue(st.flow())

        self.assertEqual(2, len(fs.get_data()))


if __name__ == '__main__':
    unittest.main()