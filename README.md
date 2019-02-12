# AtraxiFlow
AtraxiFlow - Flexible python workflow tool

**Example**

```python
from Stream import Stream, axflow_start
from nodes.EchoOutputNode import EchoOutputNode

axflow_start()

Stream \
    .create() \
    .append_node(EchoOutputNode(props='Hello World')) \
    .run()
```
