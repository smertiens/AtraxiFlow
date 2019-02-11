from nodes.foundation import ProcessorNode


class NullNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {}
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def run(self, stream):
        pass
