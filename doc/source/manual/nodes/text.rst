Text processing nodes
=====================

TextFileInputNode
*****************

This node reads from a textfile and outputs the contents to a new :ref:`textres`.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - filename
     - The path to a textfile to read from
     - Yes
   * - resource_name
     - The name the resource that will hold the file's contents. An error will occur if that name already exists
     - No. Defaults to "last_textfile_contents"

**Output**

The newly created TextResource with the file contents.

**Example**

.. code-block:: python

    from atraxiflow.nodes.text import *
    from atraxiflow.core.stream import *

    st = Stream()
    node = TextFileInputNode({
        'filename': file,
        'resource_name': 'file_content'
    })
    st >> node >> flow()

    # will read the input of 'file' and save it to a resource 'file_content'


TextFileOutputNode
*****************

This node writes TextResources to a textfile.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - filename
     - The textfile to write to
     - Yes
   * - sources
     - A :ref:`resfilters` that queries the TextResources that should be written
     - No. Defaults to "Text:*"
   * - newline_per_res
     - if True, when writing multiple resources, a newline will be added after each resources output
     - No. Defaults to True

**Example**

.. code-block:: python

    st = Stream()
    res1 = TextResource('part1', {'text': 'Hello'})
    res2 = TextResource('part2', {'text': 'World'})

    node = TextFileOutputNode({
        'filename': file,
        'sources': 'Text:*'
    })
    st >> res1 >> res2 >> node

    assert st.flow()

    # The contents of 'file' will be:
    #
    # Hello
    # World


TextValidatorNode
*****************

This node validates a TextResource given a list of rules.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - sources
     - A resource query that tells the node which TextResources to consider for validation (see also :ref:`resfilters`)
     - No (defaults to 'Text:\*')
   * - rules
     - A dictionary with rules for validation
     - No. Defaults to an empty dictionary


**Supported rules**

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

**Output**

None

**Example**

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