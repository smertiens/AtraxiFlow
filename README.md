# AtraxiFlow
The flexible python workflow tool

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=master)](https://travis-ci.org/smertiens/AtraxiFlow)

* Create easy-to-read automation scripts in minutes
* Allows you to create your own nodes and resources
* Requires at least python 3.4

**Changes in 1.0.0b3**

* Added additional filters to FileFilterNode (see: [online documentation](https://docs.atraxi-flow.com/manual/nodes.html#filefilternode))

**Learn**

* Read more about [the concept](https://docs.atraxi-flow.com/basics.html)
* Get started using [the online documentation](https://docs.atraxi-flow.com/index.html)

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
