Nodes
=====

Nodes will process your data and also create the output of your script (see :doc:`/basics` for more).
You can create nodes in different ways. The most common one is this:

.. code-block:: python

    from atraxiflow.nodes.common import EchoOutputNode

    node = EchoOutputNode('my_node', {'msg': 'Hello World'})


If you only provide one argument, it will be interpreted as the node name when it's a string or as settings
when it's a dictionary.

.. code-block:: python

    # Creates a node with the given settings and an empty name (nodes do not require a name, unless you
    # want to reference them later
    node = EchoOutputNode({'msg' : 'Hello World'})

    # this will create a named node with default settings
    node = EchoOutputNode('my_node')

    # you can also set the node properties after creating the node...
    node.set_property('msg', 'Hello World')

    # ... and also read it
    msg = node.get_property()

    # most nodes also provide an output (see the node's documentation for more information)
    output = node.get_output()


.. toctree::
    :maxdepth: 2
    :caption: Built-in nodes:

    common
    filesystem
    text
    gui
    graphics