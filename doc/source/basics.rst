The concept
***********

AtraxiFlow is a workflow tool for Python. It is meant to be simple, inuitive and
flexible. Everyone familiar with basic python scripting should be able to create
complex workflows without reading extensive API docs or manuals.

AtraxiFlow consists of three major elements: :ref:`manual/streams`, :ref:`manual/nodes` and :ref:`manual/resources`.
The following image will help you understand how they work together:

**Streams** are the basic building blocks. They hold all other components. Think of them as
a stream of water, like a river. They will take you from the start of your script to your destination
(= the result of your workflow).

**Resources** provide things you can work with in your stream, for example Files, Images, Texts or
more complex things like data from a database or the internet. Resources have different
*properties* that determine how they behave or where they should get their data from.
The :ref:`FilesystemResource` for example has a *sourcePattern*-Property. You can set it to
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

