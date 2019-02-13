from atraxiflow.Stream import Stream, axflow_start
from atraxiflow.nodes.EchoOutputNode import EchoOutputNode

axflow_start()

Stream \
    .create() \
    .append_node(EchoOutputNode(props='Hello World')) \
    .run()
