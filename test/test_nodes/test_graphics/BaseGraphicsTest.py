#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest
from PIL import Image


class BaseGraphicsTest(unittest.TestCase):

    def create_test_image(self, path, w=800, h=600):
        img = Image.new('RGB', (w, h))
        img.save(path)
