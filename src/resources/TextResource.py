from resources.Resource import *

class TextResource(Resource):

    _known_properties = {
        'text': {
            'label': "Text",
            'type': "string",
            'required': False,
            'hint': 'A simple text',
            'default': ''
        }
    }

    def getPrefix(self):
        return 'Text'

    def setText(self, text):
        self.setProperty('text', text)

    def toString(self):
        return self.getProperty('text')

