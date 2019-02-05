import Stream, StreamRunner
from nodes.ShellExecNode import ShellExecNode

if __name__ == '__main__':
    st = Stream.Stream()
    runner = StreamRunner.StreamRunner()

    root = ShellExecNode("nodeExec", {"cmd": "sphinx-build source build"})
    runner.run(st, root)