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


def test_resize_and_output(tmpdir):
    for i in range(1, 4):
        Image.new('RGB', (800, 600)).save(str(tmpdir.join('img{0}.jpg'.format(i))))

    st = Stream()
    img1 = ImageResource({'src': str(tmpdir.join('img1.jpg'.format(i)))})
    img2 = ImageResource({'src': str(tmpdir.join('img2.jpg'.format(i)))})
    img3 = ImageResource({'src': str(tmpdir.join('img3.jpg'.format(i)))})

    st.add_resource(img3)
    st.add_resource(img2)
    st.add_resource(img1)

    assert 3 == len(st.get_resources('Img:*'))

    node = ImageResizeNode({'target_w': '300'})
    node.connect(img3, 'sources')
    node.connect(img2, 'sources')
    node.connect(img1, 'sources')
    st.append_node(node)

    out_node = ImageOutputNode({'output_file': str(tmpdir.join('{img.src.basename}_test.{img.src.extension}'))})
    out_node.connect(img3, 'sources')
    out_node.connect(img2, 'sources')
    out_node.connect(img1, 'sources')

    st.append_node(out_node)

    assert st.flow()

    for i in range(1, 4):
        assert os.path.exists(str(tmpdir.join("img{0}_test.jpg".format(i))))
        imgtmp = Image.open(str(tmpdir.join("img{0}_test.jpg".format(i))))
        assert 300 == imgtmp.size[0]
