# AtraxiFlow
The flexible python workflow tool

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=develop)](https://travis-ci.org/smertiens/AtraxiFlow)

Documentation and PIP package will be available as soon as initial testing is complete.

* Easy and readable
* Write your own nodes within minutes
* No dependencies (unless you want to use the ImageProcessing nodes :)
* Requires at least python 3.4

**Install**
```
pip install atraxi-flow
```

**Example**

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
