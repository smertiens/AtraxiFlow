#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import sys, os

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'src'))
print('Adding atraxiflow to path: ', path)
sys.path.insert(0, path)