from atraxiflow.core.stream import Stream
from atraxiflow.nodes.common import EchoOutputNode
from atraxiflow.gui import *

st = Stream \
    .create() \
    .append_node(EchoOutputNode(props='Hello World'))

gui = GUI(st)
gui.flow()