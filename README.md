# AtraxiFlow
The flexible python workflow tool

**Install**
```
pip install atraxi-flow
```

**Usage**

```python
from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode

Stream.create().append_node(EchoOutputNode({'msg': 'Hello World'})).flow()

```
