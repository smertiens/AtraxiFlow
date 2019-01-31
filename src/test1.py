import logging
from nodes import FSCopyNode
from resources.FilesystemResource import *
from Stream import *
from StreamRunner import *

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    st = Stream()
    sr = StreamRunner()
    st.addResource(FilesystemResource('../playground/fold1'))

    root = FSCopyNode.FSCopyNode({'dest': '../playground/fold3'})
    sr.run(st, root)