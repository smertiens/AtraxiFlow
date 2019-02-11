from nodes.foundation import Resource
from common.graphics import ImageObject
from common.propertyobject import PropertyObject

class ImageResource(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'file': {
                'label': "Source",
                'type': "file",
                'required': True,
                'hint': 'An image file',
                'default': '',
                'primary': True
            }
        }
        self.children = []
        self.listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

        # node specific
        self._imgobject = None

        self.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self.event_property_changed)

    def event_property_changed(self, data):
        if data == 'file':
            self._imgobject = ImageObject(self.get_property('file'))

    def get_prefix(self):
        return 'Img'

    def remove_data(self, obj):
        self._imgobject = None

    def get_data(self, key=""):
        self.check_properties()

        return self._imgobject
