import logging, sys
from nodes import FSCopyNode, CLIInputNode,EchoOutputNode,NullNode
from resources.FilesystemResource import *
from Stream import *
from StreamRunner import *

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.disable(logging.CRITICAL)

    st = Stream()
    sr = StreamRunner()
    root = CLIInputNode.CLIInputNode("cli", {"save_to": "username", "prompt": "Enter your name"})
    n2 = EchoOutputNode.EchoOutputNode("echo", {"text": "Your name is {Res::Text:username}"})
    root.addChild(n2)

    sr.run(st, root)