#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from nodes.foundation import ProcessorNode
from nodes.graphics.ImageResource import ImageResource
from nodes.FilesystemResource import FilesystemResource
from common import graphics
import logging


class ImageResizeNode(ProcessorNode):

    def __init__(self, name="", props=None):

        self.name = name
        self._known_properties = {
            'target_w': {
                'label': "New width",
                'type': "text",
                'required': False,
                'hint': '',
                'default': 'auto'
            },
            'target_h': {
                'label': "New height",
                'type': "text",
                'required': False,
                'hint': '',
                'default': 'auto'
            },
            'source': {
                'label': "Resources to use",
                'type': "text",
                'required': False,
                'hint': '',
                'default': ''
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def _do_resize(self, img):
        # Calculate final size
        w = self.get_property('target_w')
        h = self.get_property('target_h')

        if w == 'auto' and h == 'auto':
            logging.error('Only one dimension (width or height) can be set to "auto" at the same time.')
            return img
        elif w == 'auto':
            w = int(h) * (img.width() / img.height())
        elif h == 'auto':
            h = int(w) * (img.height() / img.width())

        new_img = img.get_image_object().resize((int(w), int(h)))
        img.set_image_object(new_img)
        return img

    def run(self, stream):
        if not graphics.check_environment():
            return False

        if not self.check_properties():
            return False

        # Get resources for transform

        # Get file resources
        res = []

        if self.get_property('source') != '':
            res += stream.get_resources(self.get_property('source'))
        else:
            res += stream.get_resources('FS:*')
            res += stream.get_resources('Img:*')

        for r in res:
            if isinstance(r, ImageResource):
                img = self._do_resize(r.get_data())
                r.update_data(img)
            elif isinstance(r, FilesystemResource):
                for fso in r.get_data():
                    img = graphics.ImageObject(fso)

                    if img.is_valid():
                        img = self._do_resize(img)

                        # we will leave the FSResources and create new ImageResources for our results
                        stream.add_resource(ImageResource(props={'src': img}))
