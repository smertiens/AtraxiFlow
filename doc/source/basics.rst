The concept
***********

The Stream
==========

Nodes
=====
All data that the node works on is supplied via an input. A Node can have unlimited inputs.
A node's output or a resource can be connected to a specific input via the input's name.
If no input name is specified, the **"primary" input** is used (the first input that has primary=True).
This helps in keeping code short and clean. For example a FileCopy node would probably expect a list of files to
copy as it's primary input.

If no primary input is set and no input name is specified, the "default" input is used.
This input merely serves as a connector between nodes, so they are executed in order.
For example an EchoNode that prints a message to the screen, would be connected via the default input,
so the message is printed after the previous node has finished. The node itself would not expect to
receive anything via the default input (the message to print could be set as a property).

How a node performs a task is set by it's properties.

Every node has an output. The output is a list of resources. It can be empty, if the node does not have an output.

Resources
=========
All data is passed between nodes as resources. This means, that all inputs expect resources and all nodes output resources.
A resource can be simple and for example contain a single number or more complex and for example contain a list of files and folders.
Resources can be added to the stream. They can then be queried with resource queries. A TextResource for example could be added to the stream and it's content be used as a variable in a string property.
When resources are set as an input to a node, they do not need to be added to the stream, since the node will discover them through the input.


OLD TEXT:


AtraxiFlow is a workflow tool for Python. It is meant to be simple, inuitive and
flexible. Everyone familiar with basic python scripting should be able to create
complex workflows without reading extensive API docs or manuals.

AtraxiFlow consists of three major elements: :doc:`/manual/streams`, :doc:`/manual/nodes` and :doc:`/manual/resources`.
The following image will help you understand how they work together:

**Streams** are the basic building blocks. They hold all other components. Think of them as
a stream of water, like a river. They will take you from the start of your script to your destination
(= the result of your workflow).

**Resources** provide things you can work with in your stream, for example Files, Images, Texts or
more complex things like data from a database or the internet. Resources have different
*properties* that determine how they behave or where they should get their data from.
The :ref:`fsres` for example has a *src*-Property. You can set it to
a file like "/hello/world.txt". You can now access the file at anytime using the stream.
So you can throw any resource into your stream and fish it out any time you need it.

**Nodes** Nodes are the workers of AtraxiFlow. You can put them anywhere in your stream and they willm use
the resources they find to do their job. Every node represents one step in your workflow.
Nodes, like resources, have properties that change the way they behave. They can change existing
resources (e.g. an ImageResizeNode will change the size of an ImageResource) or add new ones
(the ImageResizeNode will also read file resources if they are images and create new ImageResources
from them).

There are basically three types of nodes. Most nodes are **ProcessorNodes**, they "do" stuff, like image resizing or
file copying. The second type of nodes are **InputNodes**, they will let you
add data interactively while running your workflow (for example let you input something in the terminal).
The last type of nodes are **OutputNodes**. They let you output the results of your workflow to a file or e.g. a server.

Here is a concept of a simple example for a stream, that will create thumbnails: ::

    FilesystemResource (will load files) -> ImageResize (to width = 300 pixels) -> ImageOutput (thumbnail_x.jpg)

