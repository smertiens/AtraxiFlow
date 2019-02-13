# AtraxiFlow
The flexible python workflow tool

**Install**
```
pip install atraxi-flow
```

**Usage**

```python
from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode, DelayNode

stream = Stream()
stream.append_node(EchoOutputNode({'msg': 'Hello World'}))
stream.flow()

# Or even easier:
Stream.create() >> EchoOutputNode({'msg': 'Wait for it..'}) >> DelayNode() >> EchoOutputNode({'msg': 'There it is!'}) >> flow()
```
