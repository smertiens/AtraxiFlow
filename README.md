# AtraxiFlow 2.0
The flexible python workflow tool

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=develop)](https://travis-ci.org/smertiens/AtraxiFlow)
[![Documentation Status](https://readthedocs.org/projects/atraxiflow/badge/?version=latest)](https://atraxiflow.readthedocs.io/en/latest/?badge=latest)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/smertiens/AtraxiFlow.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/smertiens/AtraxiFlow/context:python)
[![PyPI version](https://badge.fury.io/py/atraxi-flow.svg)](https://badge.fury.io/py/atraxi-flow)

AtraxiFlow 2.0 will not be backward-compatible, existing nodes can still be easily rewritten. Some of the new key features
are:

* Simpler node structure  that result in even shorter scripts
* Introduction of inputs and outputs
* AtraxiCreator has been completely rewritten and is now a part of the AtraxiFlow Core package
* Streams are now called Workflows
* Improved logging

---

* Create easy-to-read automation scripts in minutes - work with files, folders, images or anything else 
* Add your own logic as AtraxiFlow node and share it with others
* Use a console for in- and output or add one of the UI nodes to show graphical messages and input forms 
built with Qt5

**Learn**

* See what you can do and check out the [examples](https://github.com/smertiens/AtraxiExamples)
* Get started with the [user manual](https://atraxiflow.readthedocs.io/en/latest/manual)
* Learn how to write your own nodes in minutes with the [developer manual](https://atraxiflow.readthedocs.io/en/latest/dev)

**Install**
```
pip install atraxi-flow
```

**Requirements**

* Python 3.5 or higher
* If you want to use the UI nodes and functions, you will need a graphical environment

**Latest Changes**

_1.0.3:_ New nodes: TextFileInputNode, TextFileOutputNode. Fixes for ShellExecNode on Windows. New convenience node-function: "echo()".

_1.0.2:_ Fixes in DateTimeProcessor and improved file date/time comparison in FileFilterNode

_1.0.1:_ ShellExecNode: new options "echo_command" and "echo_output"

_1.0.0:_ First production release  

