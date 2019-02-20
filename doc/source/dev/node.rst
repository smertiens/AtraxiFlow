Writing nodes
=============

In this part we will look at creating a new node for AtraxiFlow. You might want to write your own nodes to use
your own business logic in AtraxiFlow or use another API. Since your node will consist of only one file (unless you
decide to use more files), you can easily share nodes with other users.

As an example, we will create a new Node that compares the number of files in two FilesystemResources and presents
the result in a customizable messsage to the user.


Creating and loading node files
-------------------------------

Nodes are simple Python files with a Node-Class in them. They are named in CamelCase and should have the suffix "Node".
Let's start with our file count comparison node by creating a new file named **FileCountComparisonNode.py**.
To use our node in a script it has to be in the *pythonpath*, like any other python module.
If you don't want to take care of modifying the pythonpath, you can save node files to AtraxiFlow's **node folder**
in the users home directory:

* On Linux/OSX: *UserHomeDirectory*/.atraxi-flow/nodes
* On Windows: *UserHomeDirectory*/atraxi-flow/nodes


Basic node skeleton
-------------------

.. code-block:: python

    from atraxiflow.nodes.foundation import ProcessorNode

    class FileCountComparisonNode(ProcessorNode):

        def __init__(self, name="", props=None):
            self._known_properties = {}
            self._listeners = {}

            self.name, self.properties = self.get_properties_from_args(name, props)

        def run(self, stream):
            self.check_properties()
            print ("Hello World!")
            return True

This code shows us some of the basic concepts behind AtraxiFlow:

* Import the ProcessorNode class, every node inherits from one the three parent node classes (see :ref:`basics`)
* The node class can have the same name as the file but it doesn't have to
* Every node needs to override the :py:meth:`constructor` and the :py:meth:`run()` method


.. code-block:: python

    def __init__(self, name="", props=None):
            self._known_properties = {}
            self._listeners = {}


The constructor receives to arguments: the name of the node to be created and a dictionary with the nodes properties.
You also have to create :py:attr:`self._known_properties` that holds all information about the properties that the node
recognizes (see below) and  :py:attr:`self._listeners` that holds the references to the classes listeners. You won't
usually use this attribute directy (see :ref:`utils`).

.. code-block:: python

    self.name, self.properties = self.get_properties_from_args(name, props)

In this line the nodes name and properties are assigned. This function is used to bundle a little piece of logic that is needed
to support the different constructors of nodes, since nodes can be created using two, one or none arguments.
If you only supply one argument it will either be assigned as a node name or as node properties, depending on wether it's
a string or dictionary.

.. code-block:: python

    def run(self, stream):
            self.check_properties()
            print ("Hello World!")
            return True

The :py:meth:`run()` method is responsible for exectuting your nodes business logic. It is called by the stream when it's
your nodes turn to be processed. The run method should always return a :py:obj:`boolean` reflecting wether the node
execution was successful (True) or not (False). If the node returns *false*, the processing of the stream will be stopped
and the :py:meth:`flow()` method will return *False*
Before using your nodes properties, you should call :py:meth:`self.check_properties()`. This will ensure all required
properties are set (or stop processing with an error) and all empty properties are filled with their default values.


Managing node properties
------------------------

Node properties are defined by adding them to :py:attr:`self._known_properties`, the key is the property name (that will
be used to assign/read the property value) and a dictionary that describes the property.
With our demo project in mind, let's define a new property *res1*, that will hold a resource query (see :ref:`resfilters`) to tell the node which
FilesystemResource to use for comparison and a property *res2* that will tell the node which FilesystemResource to
compare with.

.. code-block:: python

    self._known_properties = {
        'res1': {
            'label': 'Resource query 1',
            'type': 'string',
            'required': False,
            'hint': 'A resource query to use for comparison',
            'default': 'FS:*'
        },
        'res2': {
            'label': 'Resource query 2',
            'type': "string",
            'required': False,
            'hint': 'Another resource query to compare to',
            'default': 'FS:*'
        }
    }


* **required** This is a boolean value. If it is true and the property is not set it, node execution will fail
* **default** If the property is not required and empty, it will be set to this default value
* *label*: A label for this property. Reserved for future use.
* *type*: one or more allowed types for this property (string, bool, number, image, list; | means "or"). Reserved for future use.
* *hint*: A short description of the property.  Reserved for future use.

You can access your nodes properties later by using :py:meth:`self.get_property()` and set a property manually by using
:py:meth:`self.set_property()`.


