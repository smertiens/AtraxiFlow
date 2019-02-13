#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.nodes.graphics.ImageResizeNode import ImageResizeNode
import unittest, os
from atraxiflow.Stream import Stream
from atraxiflow.nodes.FilesystemResource import FilesystemResource
from atraxiflow.nodes.graphics.ImageResource import ImageResource
from test.test_nodes.test_graphics.BaseGraphicsTest import BaseGraphicsTest

class test_ImageResizeNode(BaseGraphicsTest):

    def tearDown(self):
        for i in range(1, 4):
            os.unlink(os.path.join(self.get_test_folder(), "img{0}.jpg".format(i)))
        os.rmdir(self.get_test_folder())

    def setUp(self):
        os.makedirs(self.get_test_folder())
        for i in range(1, 4):
            self.create_test_image(os.path.join(self.get_test_folder(), "img{0}.jpg".format(i)))

    def get_test_folder(self):
        return os.path.realpath(os.path.join(os.getcwd(), "_temp"))

    def test_create_and_env_check(self):
        st = Stream()
        node = ImageResizeNode()
        st.append_node(node)
        self.assertTrue(st.run())

    def test_load_resources(self):
        st = Stream()
        st.add_resource(FilesystemResource(props={'sourcePattern': os.path.join(self.get_test_folder(), 'img1.jpg')}))
        st.add_resource(FilesystemResource(props={'sourcePattern': os.path.join(self.get_test_folder(), 'img2.jpg')}))
        st.add_resource(ImageResource(props={'src': os.path.join(self.get_test_folder(), 'img3.jpg')}))
        self.assertEqual(2, len(st.get_resources('FS:*')))
        self.assertEqual(1, len(st.get_resources('Img:*')))

        st.append_node(ImageResizeNode(props={'target_w' : '300'}))
        self.assertTrue(st.run())

        self.assertEqual(2, len(st.get_resources('FS:*')))
        self.assertEqual(3, len(st.get_resources('Img:*')))


if __name__ == '__main__':
    unittest.main()
