Resources
=========

Resource will let you add files, images and other things to your stream.
They can be changed and also created by nodes while your workflow runs.
If you cannot find a suitable resource, you can create your own one in no time.

FilesystemResource
******************

This resource loads files and folders from your local computer.

Properties
----------

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - sourcePattern
     - The file or folder you want to load. You can use wildcards. The resource will automatically
       create a proper list of files and folders
     - Yes

Example
-------

.. code-block:: python

    from nodes.FilesystemResource import FilesystemResource

    fs_res = Filesystemresource("my_images", {'sourcePattern' : '/hello/world/*.jpg'})



ImageResource
*************

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

    from nodes.graphics.ImageResource import ImageResource

    img_res = ImageResource("image", {'src' : '/hello/world/myimage.jpg'})


TextResource
************

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

    from nodes.TextResource import TextResource

    img_res = TextResource("mytext", {'text' : 'Hello World!'})

