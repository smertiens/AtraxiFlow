Graphics nodes
==============

ImageResizeNode
***************

Resizes images.

**Properties**

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
     - A resource query that tells the node which ImageResources to consider for resizing (see also :ref:`resfilters`). The node also recognizes :ref:`fsres` as input. It will try to convert them into ImageObjects
     - No. Default: 'Img:\*'


**Output**

This node has no output.


**Example**

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

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - source
     - A resource query that tells the node which ImageResources to save out (see also :ref:`resfilters`)
     - No. Defaults to 'Img:\*'
   * - output_file
     - The filename of the images to created. You should use one of the variables listed below if you process more than one image, otherwise all the files will have the same name and thus be overwritten.
     - Yes


**Output**

This node has no output.


**Variables for output_file**

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

**Example**

.. code-block:: python

    from atraxiflow.nodes.graphics import *

    st = Stream()
    st.add_resource(ImageResource({'src': '/img_*.jpg')}))
    st.append_node(ImageResizeNode(props={'target_w': '300'}))

    # if the output folder does not exist, it will be created
    st.append_node(ImageOutputNode(props={'output_file': '/img/thumbs/{img.src.basename}.{img.src.extension}')}))


