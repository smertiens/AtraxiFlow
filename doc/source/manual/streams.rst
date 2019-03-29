Streams
=======

Streams hold all your nodes and resources and are executed sequentially. For more information on streems see
:doc:`/basics`. Executing a workflow basically means running a stream, so you will need to create at least one
Stream in you workflow script. Let's see how that works.

Creating streams and adding content
-----------------------------------

You can create Streams like any other class or use their :py:meth:`create()` function. They are equivalent, the factory
function allows for better chaining in your code (see below).

.. code-block:: python

    from atraxiflow.core.stream import *

    # create it like any other class
    stream = Stream()

    # use the factory function if you like and do not need to reference the steam again
    Stream.create().append_node(node).flow()

You can now add nodes and resources to your stream using the :py:meth:`Stream.add_resource()` and :py:meth:`Stream.append_node()`
methods. For easier readability you can use AtraxiFlows *flow syntax*.

.. code-block:: python

    from atraxiflow.core.stream import *

    stream = Stream()
    # add a resource
    stream.add_resource(TextResource())

    # add a node
    stream.append_node(NullNode())

    # the stream class supports chaining
    stream.append_node(NullNode()).append_node(NullNode())

    # flow syntax with create()
    Stream.create() >> NullNode() >> NullNode()


Run your stream
---------------

You can execute your stream using the :py:meth:`Stream.flow()` method. This will execute your nodes in the order in which
you've added them to the resource. If you are using flow syntax use he :py:func:`flow()` helper function to start the stream.

.. code-block:: python

    from atraxiflow.core.stream import *

    stream = Stream()
    stream.append_node(NullNode())

    # start stream
    stream.flow()

    # start via flow syntax
    Stream.create() >> NullNode() >> NullNode() >> flow()


Using branches for parallel processing
--------------------------------------

You can create branches on your stream using :py:meth:`Stream.branch()`. The branch will have its own stream
associated with it but inherit all resources from its parent stream.
During execution when the stream reaches a branch the branches stream is started as a separate thread.

.. code-block:: python

    from atraxiflow.core.stream import Stream
    from atraxiflow.nodes.common import DelayNode, EchoOutputNode

    stream = Stream()
    stream.append_node(EchoOutputNode({'msg': 'Already done.'}))

    # when a new branch is added it returns a reference to its stream so you can
    # start adding content right away
    stream.branch('branch_1') \
        .append_node(DelayNode({'time': 5})) \
        .append_node(EchoOutputNode({'msg': 'Branch 1 done.'}))

    stream.branch('branch_2') \
        .append_node(DelayNode({'time': 2})) \
        .append_node(EchoOutputNode({'msg': 'Branch 2 also done.'}))

    stream.flow()

You can use :py:meth:`Stream.get_branch()` to add to a branch later in your script.

.. code-block:: python

    stream.get_branch('branch_1') \
        .get_stream() \ # <- notice that we need to get the stream ourselves when we use get_branch()
        .append_node(EchoOutputNode({'msg': 'Last but not least.'}))



Running streams within a user interface
---------------------------------------

See :ref:`streamui`.
