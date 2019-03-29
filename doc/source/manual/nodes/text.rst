Text processing nodes
=====================

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