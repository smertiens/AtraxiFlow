Nodes
=====

FSCopyNode
**********

Properties
----------

Example
-------


FileFilterNode
**************

Properties
----------

Example
-------


ShellExecNode
*************

Properties
----------

Example
-------


DelayNode
*********

Properties
----------

Example
-------


EchoOutputNode
**************

This node will output a message to the console.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - msg
     - The message to output
     - No (defaults to '')

Example
-------

.. code-block:: python

    from nodes.EchoOutputNode import EchoOutputNode

    # we will create this without a name, since we usually don't need to reference it again
    text_res = EchoOutputNode(props = {'msg': 'hello world'})


NullNode
********

This node does: nothing. It is mainly used during testing. You can still use it to store and
retrieve properties (see :ref:`api/nodes`)

Example
-------

.. code-block:: python

    from nodes.NullNode import NullNode

    null_node = NullNode()
    null_node.set_property('hello_world')
    print(null_node.get_property()) # Hello World


ImageResizeNode
***************

Properties
----------

Example
-------


ImageOutputNode
***************

Properties
----------

Example
-------

