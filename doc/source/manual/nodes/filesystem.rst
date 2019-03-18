Filesystem Nodes
================

FSCopyNode
**********

This node copies files and folders on your local filesystem. You need to add a :ref:`fsres` to tell the node which files
or folders to copy.

**Properties**


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


**Output**

This node has no output.


**Example**

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

**Properties**

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
     - No Defaults to 'FS:\*' (that will fetch all FilesystemResources)


**Output**

This node outputs a list of  :ref:`fsres`, containing the matched files and folders.


**Supported fields for filtering**

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
   * - type
     - Filter for type. Supports "file" or "folder". Only takes equal-to-operator ("=")
   * - filename
     - Filters by filename (without the directory part). Supported operators: contains, startswith, endswith, matches (regex)
   * - filedir
     - Filters by directory part of files or folders (without the filename). Supports same operators as "filename".


**Example**

This will leave all files in the stream, that are larger than 120 kilobytes and smaller than 4 megabytes

.. code-block:: python

    from atraxiflow.nodes.filesystem import FileFilterNode, FilesystemResource
    from atraxiflow.core.stream import *

    node = FileFilterNode({
        'filter', [
            ['file_size', '>', '120K'],
            ['file_size', '<', '4M']
        ],
        'sources': 'FS:*'
     })

    fs = FilesystemResource({'src': '/documents/files/*'})
    Stream.create() >> fs >> node >> flow()

    filtered_resources = node.get_output()


FSRenameNode
************

This node renames files supplied by :ref:`fsres`.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - name
     - A single string that, when set, serves as the new name for the file(s). See below for variables.
     - No
   * - replace
     - A dictionary of key/value pairs to be replaced. If both name and replace are set, first the name is applied and the replacement on top of that.
     - No
   * - sources
     - A resource query that tells the node which FilesystemResources to consider for filtering (see also :ref:`resfilters`)
     - No. Defaults to 'FS:\*'


**Output**

This node outputs a list of  :ref:`fsres`, containing the renamed files and folders.


**Supported variables for name-property**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - file.path
     - The path of the original file. (/dir/test.txt -> /dir)
   * - file.basename
     - The basename of the original file (test.txt -> test)
   * - file.extension
     - The extension of the original file without period (test.txt -> txt)


**Example**


.. code-block:: python

    from atraxiflow.nodes.filesystem import FileFilterNode, FilesystemResource
    from atraxiflow.core.stream import *

    ## Example 1 ##
    res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), '*'))})

    # will put a "_something" behind every file-basename in the given directory
    node = FSRenameNode({'name': '{file.path}/{file.basename}_something.{file.extension}'})
    Stream.create()->add_resource(res)->append_node(node)->flow()


    ## Example 2 ##
    res = FilesystemResource({'src': os.path.realpath(os.path.join(self.get_test_dir(), 'testfile.txt'))})

    # as you can see, you can also use regular expressions to search for strings to be replaced
    # this will result in the filename "foobar.ext"
    node = FSRenameNode({'replace': {
        'testfile' : 'foobar',
        re.compile(r'[\.txt]+$') : '.ext'
    }})
    Stream.create()->add_resource(res)->append_node(node)->flow()

    renamed_files = node.get_output()
