#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from nodes.foundation import Resource


class TextResource(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'text': {
                'label': "Text",
                'type': "string",
                'required': False,
                'hint': 'A simple text',
                'default': ''
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def get_prefix(self):
        return 'Text'

    def get_data(self):
        return self.get_property('text', '')

    def update_data(self, text):
        self.set_property('text', text)

    def __str__(self):
        return str(self.get_property('text', ''))
