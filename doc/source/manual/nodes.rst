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



FSCopyNode
**********

This node copies files and folders on your local filesystem. You need to add a :ref:`fsres` to tell the node which files
or folders to copy.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - dest
     - The path to the destination folder
     - Yes
   * - create_if_missing
     - When set to True, the destination folder will be created if it does not exist.
     - No (default: False)

Example
-------

.. code-block:: python

    from atraxiflow.nodes.filesystem import FilesystemResource, FSCopyNode
    from atraxiflow.core.stream import Stream

    res = FilesystemResource({'src': '/hello/folder/myfile.txt'})
    node = FSCopyNode({'dest': '/hello/world'})

    Stream.create().add_resource(res).append_node(node).flow()

You can also use wildcards in the FilesystemResource, this will copy all matching files:

.. code-block:: python

    res = FilesystemResource({'src': '/hello/folder/*.txt'})


FileFilterNode
**************

This node filters files supplied by a :ref:`fsres`.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - filter
     - A dictionary with the filters that should be applied to sources
     - Yes
   * - sources
     - A resource query that tells the node which FilesystemResources to consider for filtering (see also :ref:`resfilters`)
     - No Defaults to 'FS:*' (that will fetch all FilesystemResources)


Supported fields for filtering
------------------------------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - filesize
     - Filter by filesize. You can use the exact number in bytes or a conveniance format (1K, 1M, 1G, 1T)
   * - date_created
     - Filter by the files created date. You can enter the dates as string ("12.01.2017") or use "today", "yesterday"
   * - date_modified
     - Filter by the files last modified date


Example
-------

This will remove all files from the stream, that are larger than 120 kilobytes and smaller than 4 megabytes

.. code-block:: python

    from atraxiflow.nodes.filesystem import FileFilterNode, FilesystemResource

    node = FileFilterNode({ 'filter', [
        ['file_size', '>', '120K'],
        ['file_size', '<', '4M']
    ]})

    fs = FilesystemResource({'src': '/documents/files/*'})


ShellExecNode
*************

This node executes a command and provides it's output in form of a :ref:`textres`.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - cmd
     - The command you want to run
     - Yes
   * - output
     - The name that should be assigned to the TextResource that holds the commands output ("stdout")
     - No. Default: 'last_shellexec_out'
   * - errors
     - The name that should be assigned to the TextResource that holds the commands errors ("stderr")
     - No. Default: 'last_shellexec_errors'

Example
-------

.. code-block:: python

    from atraxiflow.nodes.common import ShellExecNode

    node = ShellExecNode({
        'cmd': 'ls -la',
        'output': 'dirlisting'
    })


DelayNode
*********

This node does nothing else then halting the script execution for the given amount of time.
It's main use is in testing AtraxiFlow's multithreading capabilities.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - wait
     - The time to wait for in seconds
     - No. Default is 5 seconds


Example
-------

.. code-block:: python

    from atraxiflow.nodes.common import DelayNode

    # takes 10 seconds
    node = DelayNode({'wait': 10})

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
retrieve properties (see :doc:`/api/nodes`)

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

