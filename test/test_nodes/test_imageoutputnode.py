#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

from PIL import Image

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.filesystem import FilesystemResource
from atraxiflow.nodes.graphics import ImageOutputNode
from atraxiflow.nodes.graphics import ImageResizeNode
from atraxiflow.nodes.graphics import ImageResource


def tearDown(self):
    for i in range(1, 4):
        os.unlink(os.path.join(self.get_test_folder(), "img{0}_test.jpg".format(i)))
        os.unlink(os.path.join(self.get_test_folder(), "img{0}.jpg".format(i)))
    os.rmdir(self.get_test_folder())


def setUp(self):
    os.makedirs(self.get_test_folder())
    for i in range(1, 4):
        self.create_test_image(os.path.join(self.get_test_folder(), "img{0}.jpg".format(i)))


def test_resize_and_output(tmpdir):
    for i in range(1, 4):
        Image.new('RGB', (800, 600)).save(str(tmpdir.join('img{0}.jpg'.format(i))))

    st = Stream()
    st.add_resource(ImageResource(props={'src': str(tmpdir.join('img1.jpg'))}))
    st.add_resource(ImageResource(props={'src': str(tmpdir.join('img2.jpg'))}))
    st.add_resource(FilesystemResource(props={'src': str(tmpdir.join('img3.jpg'))}))
    assert 2 == len(st.get_resources('Img:*'))
    assert 1 == len(st.get_resources('FS:*'))

    st.append_node(ImageResizeNode(props={'target_w': '300'}))
    st.append_node(
        ImageOutputNode(props={'output_file': str(tmpdir.join('{img.src.basename}_test.{img.src.extension}'))}))

    assert st.flow()

    for i in range(1, 4):
        assert os.path.exists(str(tmpdir.join("img{0}_test.jpg".format(i))))
        imgtmp = Image.open(str(tmpdir.join("img{0}_test.jpg".format(i))))
        assert 300 == imgtmp.size[0]
