from atraxiflow.core.stream import Stream
from atraxiflow.nodes.EchoOutputNode import EchoOutputNode


if __name__ == '__main__':
    stream = Stream()
    node = EchoOutputNode('echo_node', {
        'text': 'Hello World'
    })
    stream.append_node(node)
    stream.flow()