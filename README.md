# AtraxiFlow 2.0
The flexible python workflow tool - create workflows within minutes, visually or in pure python.

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=master)](https://travis-ci.org/smertiens/AtraxiFlow)
[![PyPI version](https://badge.fury.io/py/atraxi-flow.svg)](https://badge.fury.io/py/atraxi-flow)

This is the first alpha release of AtraxiFlow 2.0. AtraxiFlow 2.0 scripts and nodes are not compatible with the 1.0
branch. Here are some of the new features:

* Simpler node structure that results in even shorter scripts
* Introduction of inputs and outputs
* AtraxiCreator has been completely rewritten and is now a part of the AtraxiFlow core package
* Streams are now called Workflows
* Improved logging

A lot of work went into rewriting the core and especially the redesign of Creator, so 
documentation of the 2.0 version is a bit behind. 
I will make tutorial videos available as soon as possible to demonstrate core features including
the creation of custom nodes. Proper online documentation will follow. For a (very basic) idea
of AtraxiFlow's ability refer to the screenshots/code samples below.

The latest 1.0 version version can be found here: https://pypi.org/project/atraxi-flow/1.0.3/

**Install**

The easiest way to install AtraxiFlow is via pip:

```
pip install atraxi-flow==2.0.0a1
```

If you want to play around with some nodes, you can start the visual workflow editor called "Creator":

```
atraxi-flow creator
```

**Build workflows visually**

You can use Creator to visually edit your workflows. Doubleclick the "workflow" item in the node list
on the left and add nodes (also by doubleclicking them). Drag the nodes close to the bottom edge of the
desired parent node to dock (and thus connect) them.

![Creator UI](https://media.atraxi-flow.com/demo_ui.png)

You can save your workflows in a way-file that can then be loaded in Creator again or be run
directly from the console.

```
atraxi-flow run demo.way
```

Wayfiles can contain more than one workflow. 

![Creator UI](https://media.atraxi-flow.com/demo_console.png)


**Build workflows in pure python**

```python
from atraxiflow.core import *
from atraxiflow.base.common import *

hello_world_node = EchoOutputNode({'msg': 'Hello World!'})
Workflow.create([hello_world_node]).run()
```

**Requirements**

* Python 3.5 or higher

**Latest Changes**

_2.0.0a1:_ First alpha release of the 2.0 branch

_1.0.3:_ New nodes: TextFileInputNode, TextFileOutputNode. Fixes for ShellExecNode on Windows. New convenience node-function: "echo()".

_1.0.2:_ Fixes in DateTimeProcessor and improved file date/time comparison in FileFilterNode

_1.0.1:_ ShellExecNode: new options "echo_command" and "echo_output"

_1.0.0:_ First production release  

