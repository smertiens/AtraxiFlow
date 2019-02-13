#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging

from atraxiflow.nodes.filesystem import FilesystemResource

from atraxiflow.core import graphics
from atraxiflow.core.graphics import ImageObject
from atraxiflow.core.properties import PropertyObject
from atraxiflow.nodes.foundation import OutputNode
from atraxiflow.nodes.foundation import ProcessorNode
from atraxiflow.nodes.foundation import Resource


class ImageResource(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'src': {
                'label': "Source",
                'type': "file,image",
                'required': True,
                'hint': 'An image file or object',
                'default': '',
                'primary': True
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

        # node specific
        self._imgobject = None

        self.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self._ev_property_changed)
        self.add_listener(PropertyObject.EVENT_PROPERTIES_CHECKED, self._ev_properties_checked)

    def _process_src(self):
        # do not process src again if imgobject is set
        # otherwise changes made by processing nodes would be overwritten
        if self._imgobject is not None:
            return

        if isinstance(self.get_property('src'), ImageObject):
            self._imgobject = self.get_property('src')
        else:
            self._imgobject = ImageObject(self.get_property('src'))

    def _ev_property_changed(self, data):
        if data == 'src':
            self._process_src()

    def _ev_properties_checked(self, data):
        if data is True:
            self._process_src()

    def get_prefix(self):
        return 'Img'

    def remove_data(self, obj):
        self._imgobject = None

    def get_data(self):
        self.check_properties()
        return self._imgobject

    def update_data(self, data):
        if not isinstance(data, ImageObject):
            logging.error("Expected ImageObject, got {0}".format(type(data)))
            return

        self._imgobject = data


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


class ImageOutputNode(OutputNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'source': {
                'label': "Source",
                'type': "text",
                'required': False,
                'hint': 'A pattern to load resources with',
                'default': ''
            },
            'output_format': {
                'label': "Output format",
                'type': "list",
                'required': False,
                'hint': '',
                'default': 'jpeg'
            },
            'output_file': {
                'label': "Output file",
                'type': "file",
                'required': True,
                'hint': 'Output path and file name. You can use variables.',
                'default': ''
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def _get_parsed_output_string(self, imgobject):
        map = {
            'img.width': imgobject.width(),
            'img.height': imgobject.height()
        }

        if imgobject.get_src():
            map['img.src.basename'] = imgobject.get_src().getBasename()
            map['img.src.extension'] = imgobject.get_src().getExtension()

        parsed_str = self.get_property('output_file')
        for varname, value in map.items():
            parsed_str = parsed_str.replace('{' + varname + '}', str(value))

        return parsed_str

    def run(self, stream):
        if not self.check_properties():
            return False

        if not graphics.check_environment():
            return False

        resources = []
        if self.get_property('source') == '':
            resources = stream.get_resources('Img:*')
        else:
            resources = stream.get_resources(self.get_property('source'))

        format = ''
        if self.get_property('output_format') == 'jpeg':
            format = graphics.ImageObject.FORMAT_JPEG

        for resource in resources:
            imgobj = resource.get_data()

            imgobj.save(self._get_parsed_output_string(imgobj), format)

        return True
