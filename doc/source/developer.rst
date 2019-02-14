Developer manual
================

Writing nodes
*************

There are three different kinds of nodes:

* Input Nodes: Offer the ability to input data and thus create resources
* Processor Nodes: Offer workflow logic and allow you to change resources
* Output Nodes: Allow you to output data to files, servers or e.g. send them as emails

Every node consists of a corresponding python class called *YourNode*nNode.py.
For Input and Output nodes, put a "Input" or "Output" in your filename (e.g. FileInputNode.py, EmailOutputNode), for processor nodes
a simple "Node" is enough.
In your file create a new class with the same name as your file. Depending on the node type you want to
create inherit one of the node classes (InputNode, OutputNode, ProcessorNode).

A basic node looks like this:

.. code-block:: python

    from nodes.OutputNode import *

    class EchoOutputNode(OutputNode):
        _known_properties = {
            'text': {
                'type': str,
                'required': True,
                'hint': 'Text to output'
            }
        }

        children = []

        def getNodeClass(self):
            return 'EchoOutput'

        def run(self, stream):
            self.check_properties()
            print(self.get_property("text"))



Add the usage of primaryProperties

