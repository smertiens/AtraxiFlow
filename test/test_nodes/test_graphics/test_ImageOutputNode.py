#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
import unittest

from Stream import Stream
from nodes.graphics.ImageResizeNode import ImageResizeNode
from nodes.graphics.ImageResource import ImageResource
from nodes.graphics.ImageOutputNode import ImageOutputNode
from nodes.FilesystemResource import FilesystemResource
from PIL import Image


class test_ImageResizeNode(unittest.TestCase):

    def tearDown(self):
        for i in range(1, 4):
            if os.path.exists(os.path.join(self.get_test_folder(), "img{0}_test.jpg".format(i))):
                os.unlink(os.path.join(self.get_test_folder(), "img{0}_test.jpg".format(i)))

    def get_test_folder(self):
        return os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "playground"))

    def test_resize_and_output(self):
        st = Stream()
        st.add_resource(ImageResource(props={'src': os.path.join(self.get_test_folder(), 'img1.jpg')}))
        st.add_resource(ImageResource(props={'src': os.path.join(self.get_test_folder(), 'img2.jpg')}))
        st.add_resource(FilesystemResource(props={'sourcePattern': os.path.join(self.get_test_folder(), 'img3.jpg')}))
        self.assertEqual(2, len(st.get_resources('Img:*')))
        self.assertEqual(1, len(st.get_resources('FS:*')))

        st.append_node(ImageResizeNode(props={'target_w' : '300'}))
        st.append_node(ImageOutputNode(props={'output_file': os.path.join(self.get_test_folder(), '{img.src.basename}_test.jpg') }))

        self.assertTrue(st.run())

        for i in range(1, 4):
            self.assertTrue(os.path.exists(os.path.join(self.get_test_folder(), "img{0}_test.jpg".format(i))))
            imgtmp = Image.open(os.path.join(self.get_test_folder(), "img{0}_test.jpg".format(i)))
            self.assertEqual(300, imgtmp.size[0])


if __name__ == '__main__':
    unittest.main()
