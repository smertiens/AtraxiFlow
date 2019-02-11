from common.propertyobject import PropertyObject


class Node(PropertyObject):

    def get_name(self):
        return self.name

    def add_child_node(self, node):
        self.children.append(node)

    def remove_child_node(self, index):
        self.children.remove(index)

    def run(self, stream):
        raise Exception("Node class must implement run-method")


class ProcessorNode(Node):
    pass


class OutputNode(Node):
    pass


class InputNode(Node):
    pass

class Resource (PropertyObject):

    def get_name(self):
        return self.name;

    def get_prefix(self):
        raise Exception("Resources must overwrite getPrefix()")

    def get_data(self, key):
        return self.get_property(key, None)

    def resolve_variable(self, varname):
        return str(self)