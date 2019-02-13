#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import sys, os

lib = os.path.realpath(os.path.join('.', '..', 'src'))

if lib not in sys.path:
    sys.path.append(lib)
