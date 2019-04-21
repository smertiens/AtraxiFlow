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
    res = ImageResource()
    node = ImageResizeNode()
    node.connect(res, 'sources')
    st.append_node(node)
    assert st.flow()


def test_load_resources(tmpdir):
    st = Stream()

    for i in range(1, 4):
        Image.new('RGB', (800, 600)).save(str(tmpdir.join('img{0}.jpg'.format(i))))

    fs1 = FilesystemResource(props={'src': str(tmpdir.join('img1.jpg'.format(i)))})
    fs2 = FilesystemResource(props={'src': str(tmpdir.join('img2.jpg'.format(i)))})
    img1 = ImageResource(props={'src': str(tmpdir.join('img3.jpg'.format(i)))})

    st.add_resource(fs1)
    st.add_resource(fs2)
    st.add_resource(img1)

    assert 2 == len(st.get_resources('FS:*'))
    assert 1 == len(st.get_resources('Img:*'))

    node = ImageResizeNode(props={'target_w': '300'})
    node.connect(fs1, 'sources')
    node.connect(fs2, 'sources')
    node.connect(img1, 'sources')
    st.append_node(node)
    assert st.flow()

    assert 2 == len(st.get_resources('FS:*'))
    assert 3 == len(st.get_resources('Img:*'))
