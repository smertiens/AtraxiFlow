#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os

def get_asset(path):
    dirname = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(dirname, path))