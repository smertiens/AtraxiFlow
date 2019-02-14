from atraxiflow.nodes.foundation import Resource


class {# ClassName #}(Resource):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {}
        self._stream = None
        self._listeners = {}

        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_prefix(self):
        return 'PREFIX'

    def remove_data(self, obj):
        # remove data
        pass

    def update_data(self, data):
        pass

    def get_data(self, key=""):
        self.check_properties()

        # get data
        return self.get_property(key)
