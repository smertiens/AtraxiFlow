from nodes.graphics.ImageResizeNode import ImageResizeNode
import unittest
from Stream import Stream

class test_ImageResizeNode(unittest.TestCase):

    def test_create_and_env_check(self):
        st = Stream()
        node = ImageResizeNode()
        st.append_node(node)
        self.assertTrue(st.run())


if __name__ == '__main__':
    unittest.main()
