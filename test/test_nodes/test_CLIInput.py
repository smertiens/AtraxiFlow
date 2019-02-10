import unittest, logging
from nodes.CLIInputNode import *
from Stream import Stream

class test_CLIInput(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)

    def test_cli_input(self):
        st = Stream()
        n = CLIInputNode("cli", {"prompt": "Enter your name", "save_to": "user_name"})



if __name__ == '__main__':
    unittest.main()
