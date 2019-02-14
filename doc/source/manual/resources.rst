Resources
=========

Resource will let you add files, images and other things to your stream.
They can be changed and also created by nodes while your workflow runs.
If you cannot find a suitable resource, you can create your own one in no time.

.. _resfilters:

Resource queries
****************

You can add as many resources to your stream as you like. Some nodes will use all resources of a certain type
when processing others allow you to define the resources you like to be processed.
If you want to reference a resource later in your workflow, you should give it a unique **name**.
Then you can use **resource queries** to access this specific resource.

Every query consists of to parts, the **resource prefix** and the **key**. The prefix is unique to every resource
type (you can find the below prefixes in the parentheses behind the resource name). Prefixes let AtraxiFlow know,
what kind of resource you are looking for. The key is usually the resource name.

.. list-table:: Examples
   :header-rows: 1

   * - Format
     - Description
   * - FS:*
     - This will return all FilesystemResources
   * - Img:*
     - This will return all ImageResources
   * - FS:my_resource
     - This will return the FilesystemResource with the name 'my_resource'
   * - FS:backup*
     - Returns all FilesystemResources whose names start with 'backup'
   * - DB:mydb.users.1
     - *For future use*: This will find a resource called "mydb" and then query "users.1". At the moment none of the standard resources use these extended keys, but they might in the future.


**Usage examples**

.. code-block:: python

    from atraxiflow.nodes.filesystem import FileFilterNode, FilesystemResource

    # the FileFilterNode lets decide on which resources you want the filters to be applied
    node = FileFilterNode({ 'sources': 'FS:images'}) # will only filter files from the resource 'images'


.. _fsres:

FilesystemResource (FS)
***********************

This resource loads files and folders from your local computer.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - src
     - The file or folder you want to load. You can use wildcards. The resource will automatically
       create a proper list of files and folders
     - Yes

Example
-------

.. code-block:: python

    from atraxiflow.nodes.filesystem import FilesystemResource

    fs_res = Filesystemresource("my_images", {'src' : '/hello/world/*.jpg'})


.. _imgres:

ImageResource (Img)
*******************

This resource represents an image. Usually images are loaded from disk by this resource.

Properties
----------

.. list-table::
    :header-rows: 1

    * - Name
      - Description
      - Required

    * - src
      - A path to an image file (a String or an :class:`common.filesystem.FSObject`)
      - Yes


Example
-------

.. code-block:: python

    from atraxiflow.nodes.graphics import ImageResource

    img_res = ImageResource("image", {'src' : '/hello/world/myimage.jpg'})


.. _textres:

TextResource (Text)
*******************

This resource represents a simple text.

Properties
----------

.. list-table::
    :header-rows: 1

    * - Name
      - Description
      - Required
    * - text
      - The text to be stored in the resource
      - No (defaults to '')


Example
-------

.. code-block:: python

    from atraxiflow.nodes.text import TextResource

    img_res = TextResource("mytext", {'text' : 'Hello World!'})

