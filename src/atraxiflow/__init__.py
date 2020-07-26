#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from atraxiflow.axlogging import *
from atraxiflow import util
import logging


__version__ = '2.0.0a1'

if util.is_debug():
    setup_loggers(logging.DEBUG)
else:
    setup_loggers()
