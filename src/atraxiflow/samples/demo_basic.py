from atraxiflow.core.stream import Stream
from atraxiflow.nodes.echooutputnode import EchoOutputNode

Stream \
    .create() \
    .append_node(EchoOutputNode(props='Hello World')) \
    .flow()
