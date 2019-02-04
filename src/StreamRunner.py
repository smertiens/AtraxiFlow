import logging

class StreamRunner:
    
    _stream = None
    _nodeCount = 0

    def loadFromFile(self, filename):
        pass

    def run(self, stream, root_node):
        logging.info("Starting processing")
        self._stream = stream
        self._runNode(root_node)
        logging.info("Finished processing {0} nodes".format(self._nodeCount))

    def _runNode (self, node):
        self._nodeCount += 1
        logging.info("Running {0}".format(node.getNodeClass()))
        node.run(self._stream)

        # Run child nodes
        for child in node.children:
            self._runNode(child)
