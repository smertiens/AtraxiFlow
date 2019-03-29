# AtraxiFlow
The flexible python workflow tool

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=master)](https://travis-ci.org/smertiens/AtraxiFlow)

* Create easy-to-read automation scripts in minutes - work with files, folders, images or anything else 
* Add your own logic as AtraxiFlow node and share it with others
* Use a console for in- and output or add one of the UI nodes to show graphical messages and input forms 
built with Qt5

**Learn**

* See what you can do and check out the [examples](https://github.com/smertiens/AtraxiExamples)
* Get started with the user manual [user manual](https://docs.atraxi-flow.com/manual/index.html)
* Learn how to write your own nodes in minutes with the [developer manual](https://docs.atraxi-flow.com/dev/index.html)

**Install**
```
pip install atraxi-flow
```

**Requirements**

* Python 3.4 or higher
* If you want to use the UI nodes and functions, you will need to install [Pyside2](https://pypi.org/project/PySide2/) (optional)

**Latest Changes**

_1.0.0: First production release_  


**Example script**

```python
from atraxiflow.nodes.common import CLIInputNode, EchoOutputNode
from atraxiflow.nodes.text import TextValidatorNode
from atraxiflow.core.stream import *

get_name = CLIInputNode('node', {'prompt': "What's your name? ", 'save_to': 'username' })
get_greeting = CLIInputNode('node', {'prompt': "And your favourite greeting? ", 'save_to': 'usergreeting' })

# let's make sure we have a name and a greeting
check_input = TextValidatorNode({'sources': 'Text:user*', 'rules': {'not_empty': {}}})
out = EchoOutputNode({'msg': '{Text:usergreeting} {Text:username}, nice to meet you!'})

# let's go!
Stream.create() >> get_name >> get_greeting >> check_input >> out >> flow()
```
