Common nodes
============

ShellExecNode
*************

This node executes a command and provides it's output in form of a :ref:`textres`.

**Properties**

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

**Output**

The node will output stdout and stderr as TextResources.

**Example**

.. code-block:: python

    from atraxiflow.nodes.common import ShellExecNode

    node = ShellExecNode({
        'cmd': 'ls -la',
        'output': 'dirlisting'
    })

ExecNode
********

This node executes a python function.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - callable
     - The function you want the node to execute
     - Yes

**Output**

The node's output will be the return value of the function you supplied.

**Example**

You can use the ExecNode for debugging inside your stream for example.

.. code-block:: python

    from atraxiflow.core.stream import *
    from atraxiflow.nodes.common import *
    from atraxiflow.core.debug import *
    from atraxiflow.nodes.filesystem import *

    st = Stream()
    res = FilesystemResource({'src': './*'})
    debug_node = ExecNode({'callable': lambda: Debug.print_resources(st, '*')})

    st >> res >> debug_node >> flow()


DelayNode
*********

This node does nothing else then halting the script execution for the given amount of time.
It's main use is in testing AtraxiFlow's multithreading capabilities.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - wait
     - The time to wait for in seconds
     - No. Default is 5 seconds


**Output**

This node has no output.


**Example**

.. code-block:: python

    from atraxiflow.nodes.common import DelayNode

    # takes 10 seconds
    node = DelayNode({'wait': 10})

EchoOutputNode
**************

This node will output a message to the console or output the contents of a resource.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - msg
     - If this is set, the node will output this message
     - No (defaults to None)
   * - res
     - If this is set to a resource identifier the node will output the resources contents (see also :ref:`resfilters`)
     - No (defaults to None)


**Output**

This node has no output.


**Example**

.. code-block:: python

    from atraxiflow.nodes.EchoOutputNode import EchoOutputNode

    # we will create this without a name, since we usually don't need to reference it again
    text_res = EchoOutputNode(props = {'msg': 'hello world'})


NullNode
********

This node does: nothing. It is mainly used during testing. You can still use it to store and
retrieve properties.

**Example**

.. code-block:: python

    from atraxiflow.nodes.NullNode import NullNode

    null_node = NullNode()
    null_node.set_property('hello', 'world')
    print(null_node.get_property('hello')) # world

CLIInputNode
************

This node prompts the user for input on the console.

**Properties**

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


**Output**

This node will outout the text the user entered as TextResource.


**Example**

.. code-block:: python

    from atraxiflow.nodes.common import CLIInputNode, EchoOutputNode
    from atraxiflow.core.stream import *

    node = CLIInputNode('node', {
        'prompt': "What's your name? ",
        'save_to': 'username'
    })

    out = EchoOutputNode({'msg': 'Hello {Text:username}'})

    Stream.create() >> node >> out >> flow()
