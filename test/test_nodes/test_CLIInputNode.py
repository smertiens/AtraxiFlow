#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest

from atraxiflow.nodes.common import CLIInputNode


class test_CLIInputNode(unittest.TestCase):

    def test_create(self):
        node = CLIInputNode('node', {'prompt': 'Hello', 'save_to': 'world'})
        self.assertEqual('Hello', node.get_property('prompt'))
        self.assertEqual('world', node.get_property('save_to'))
