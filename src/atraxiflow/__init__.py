#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


import os, platform, logging, sys

AXF_VERSION = '1.0.3'

### Initialize environment ###

axf_user_dir = os.path.expanduser('~')

if platform.system() == 'Windows':
    axf_user_dir = os.path.join(axf_user_dir, "axtraxi-flow")
else:
    axf_user_dir = os.path.join(axf_user_dir, ".atraxi-flow")

if not os.path.exists(axf_user_dir):
    logging.debug('User dir "{0}" does not exist. Creating.'.format(axf_user_dir))
    os.makedirs(axf_user_dir)

node_dir = os.path.join(axf_user_dir, "nodes")
if os.path.exists(node_dir):
    if not node_dir in sys.path:
        sys.path.append(node_dir)
        logging.debug('Added "{0}" to path.'.format(node_dir))
else:
    logging.debug('Node dir "{0}" not found.'.format(node_dir))
