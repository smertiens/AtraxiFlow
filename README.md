# AtraxiFlow
The flexible python workflow tool

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=develop)](https://travis-ci.org/smertiens/AtraxiFlow)

Documentation and PIP package will be available as soon as initial testing is complete.

* Easy and readable
* Write your own nodes within minutes
* No dependencies (unless you want to use the ImageProcessing nodes :)

**Install**
```
It will be available via PIP as soon as the first release is out!
```

**Usage**

```python
from atraxiflow.core.stream import *
from atraxiflow.nodes.common import EchoOutputNode

Stream.create() >> EchoOutputNode({'msg': 'Hello World!'}) >> flow()
```
