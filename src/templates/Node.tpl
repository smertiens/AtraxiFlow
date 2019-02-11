from nodes.foundation import {# Type #}


class {# ClassName #}({# Type #}):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {}
        self.children = []

        if props:
            self.properties = props
        else:
            self.properties = {}

    def run(self, stream):
        self.check_properties()
        print ("Hello World!")
        return True
