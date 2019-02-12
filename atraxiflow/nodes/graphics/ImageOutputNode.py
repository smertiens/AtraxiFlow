#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from nodes.foundation import OutputNode
from common import graphics



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
