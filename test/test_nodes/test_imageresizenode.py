#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from PIL import Image

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.filesystem import FilesystemResource
from atraxiflow.nodes.graphics import ImageResizeNode, ImageResource


def test_create_and_env_check():
    st = Stream()
    node = ImageResizeNode()
    st.append_node(node)
    assert st.flow()


def test_load_resources(tmpdir):
    st = Stream()

    for i in range(1, 4):
        Image.new('RGB', (800, 600)).save(str(tmpdir.join('img{0}.jpg'.format(i))))

    st.add_resource(FilesystemResource(props={'src': str(tmpdir.join('img1.jpg'.format(i)))}))
    st.add_resource(FilesystemResource(props={'src': str(tmpdir.join('img2.jpg'.format(i)))}))
    st.add_resource(ImageResource(props={'src': str(tmpdir.join('img3.jpg'.format(i)))}))

    assert 2 == len(st.get_resources('FS:*'))
    assert 1 == len(st.get_resources('Img:*'))

    st.append_node(ImageResizeNode(props={'target_w': '300'}))
    assert st.flow()

    assert 2 == len(st.get_resources('FS:*'))
    assert 3 == len(st.get_resources('Img:*'))
