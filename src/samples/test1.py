from old import CLIInputNode
from nodes import EchoOutputNode
from Stream import *

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.disable(logging.CRITICAL)

    st = Stream()
    root = CLIInputNode.CLIInputNode("cli", {"save_to": "username", "prompt": "Enter your name"})
    n2 = EchoOutputNode.EchoOutputNode("echo", {"text": "Your name is {Res::Text:username}"})
    root.addChild(n2)
    st.appendNode(root)
    st.run()

    sr.run(st, root)