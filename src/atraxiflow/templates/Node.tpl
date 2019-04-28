# tpl::choose("type", "Choose, the type of the node name",  ("ProcessorNode", "InputNode", "OutputNode"))
# tpl::ask ("classname", "What should the classname of your node be?")
# tpl::yesno(val, "Something bool")
# tpl::filename = "$classname.py"
#% tpl::set("var", "Value")

from atraxiflow.nodes.foundation import $type


class $classname($type):

    def __init__(self, name="", props=None):
        self._known_properties = {}
        self._listeners = {}
        self._inputs = {}

        self.name, self.properties = self.get_properties_from_args(name, props)
        self._out = None

    def run(self, stream):
        self.check_properties()
        self.check_inputs()

        print ("Hello World!")
        return True

    def get_output(self):
        return self._out