from atraxiflow.nodes.foundation import {# Type #}


class {# ClassName #}({# Type #}):

    def __init__(self, name="", props=None):
        self._known_properties = {}
        self._listeners = {}

        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        self.check_properties()
        print ("Hello World!")
        return True
