import Stream
from nodes.ShellExecNode import ShellExecNode

if __name__ == '__main__':
    st = Stream.Stream()
    root = ShellExecNode("nodeExec", {"cmd": "sphinx-build source build"})
    st.appendNode(root)
    st.run()