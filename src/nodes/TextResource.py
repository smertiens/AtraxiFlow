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

        if props:
            self.properties = props
        else:
            self.properties = {}

    def get_prefix(self):
        return 'Text'

    def set_text(self, text):
        self.set_property('text', text)

    def __str__(self):
        return self.get_property('text')
