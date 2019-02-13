from atraxiflow.nodes.foundation import Resource


class {# ClassName #}(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {}
        self._children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}


    def get_prefix(self):
        return 'PREFIX'

    def remove_data(self, obj):
        # remove data
        pass

    def get_data(self, key=""):
        self.check_properties()

        # get data
        return self.get_property(key)
