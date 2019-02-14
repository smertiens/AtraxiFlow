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

    from atraxiflow.nodes.EchoOutputNode import EchoOutputNode

    # we will create this without a name, since we usually don't need to reference it again
    text_res = EchoOutputNode(props = {'msg': 'hello world'})


NullNode
********

This node does: nothing. It is mainly used during testing. You can still use it to store and
retrieve properties (see :doc:`/api/nodes`)

Example
-------

.. code-block:: python

    from atraxiflow.nodes.NullNode import NullNode

    null_node = NullNode()
    null_node.set_property('hello_world')
    print(null_node.get_property()) # Hello World


TextValidatorNode
*****************

This node validates a TextResource given a list of rules.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - sources
     - A resource query that tells the node which TextResources to consider for validation (see also :ref:`resfilters`)
     - No (defaults to 'Text:*')
   * - rules
     - A dictionary with rules for validation
     - No. Defaults to an empty dictionary


Supported rules
---------------

.. list-table::
   :header-rows: 1

   * - Rule
     - Parameters
     - Description
   * - not_empty
     - None
     - Validation will fail if the text ist empty
   * - min_len
     - length: The length to check for
     - Validation will fail if the text is shorter than *length*
   * - max_len
     - length: The length to check for
     - Validation will fail if the text is longer than *length*
   * - regex
     - pattern: The regex pattern to use (see: https://docs.python.org/3.7/library/re.html for reference)
       mode: either 'must_match' (default) or 'must_not_match'
     - Validation will fail or pass depending in the regex and mode

Example
-------

.. code-block:: python

    from atraxiflow.nodes.text import TextResource, TextValidatorNode

    text = TextResource('long', {'text': 'Hello World!'})

    node = TextValidatorNode({
        'sources': 'Text:long',
        'rules': {
            'min_len': {'length': 10}
        }
    })

    # will pass


CLIInputNode
************

This node prompts the user for input on the console.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - save_to
     - The name of the TextResource that will hold the user input. The TextResource is automatically created by the CLIInputNode
     - No (defaults to 'last_cli_input')
   * - prompt
     - The text that is shown to the user when asking for input
     - No. Defaults to 'Please enter: '

Example
-------

.. code-block:: python

    from atraxiflow.nodes.common import CLIInputNode, EchoOutputNode

    node = CLIInputNode('node', {
        'prompt': "What's your name? ",
        'save_to': 'username'
    })

    out = EchoOutputNode({'msg': 'Hello {Text:username}'})

    Stream.create() >> node >> out >> flow()

ImageResizeNode
***************

Resizes images.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - target_w
     - The new image width. If set to 'auto' the target_h will be applied, maintaining the images current aspect ratio
     -  No. Defaults to 'auto'
   * - target_h
     - The new image height. If set to 'auto' the target_w will be applied, maintaining the images current aspect ratio
     - No. Defaults to 'auto'
   * - sources
     - A resource query that tells the node which ImageResources to consider for resizing (see also :ref:`resfilters`). The node also recognizes :ref:`fsref` as input. It will try to convert them into ImageObjects
     - No. Default: 'Img:*'


Example
-------
.. code-block:: python

    from atraxiflow.nodes.graphics import ImageResizeNode, ImageResource

    st = Stream()
    st.add_resource(ImageResource({'src': '/images/*.jpg'}))

    # resizes all images to a width of 300 pixels, adjusting the height to maintain the images aspect ratio
    st.append_node(ImageResizeNode({'target_w': '300'}))
    st.flow()


ImageOutputNode
***************

Creates image files from ImageResources. The format of the resulting image file is determined by the output_files's extension (e.g. '.jpeg' will create a JPEG file)

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - source
     - A resource query that tells the node which ImageResources to save out (see also :ref:`resfilters`)
     - No. Defaults to 'Img:*'
   * - output_file
     - The filename of the images to created. You should use one of the variables listed below if you process more than one image, otherwise all the files will have the same name and thus be overwritten.
     - Yes

Variables for output_file
-------------------------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - img.width
     - The width of the image
   * - img.height
     - The height of the image
   * - img.src.basename
     - If the ImageResource was created from file: The source files basename (e.g.: File 'hello.jpg' -> Basename: 'hello')
   * - img.src.extension
     - If the ImageResource was created from file: The file extension of the source file

Example
-------

.. code-block:: python

    from atraxiflow.nodes.graphics import *

    st = Stream()
    st.add_resource(ImageResource({'src': '/img_*.jpg')}))
    st.append_node(ImageResizeNode(props={'target_w': '300'}))

    # if the output folder does not exist, it will be created
    st.append_node(ImageOutputNode(props={'output_file': '/img/thumbs/{img.src.basename}.{img.src.extension}')}))

