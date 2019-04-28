#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


import argparse
import os

import atraxiflow.core.util as util
from atraxiflow.cli.generator import TemplateParser

if __name__ == '__main__':
    # Parse CLI args
    parser = argparse.ArgumentParser(description="Flow based workflow tool")

    parser.add_argument('command', metavar='cmd', type=str, nargs='?',
                        help='The command you want to execute')

    ### create:node ###
    parser.add_argument("--name", type=str, help="The class name of the node you want to create",
                        default="NewNode")
    parser.add_argument("--type", type=str, help="The node type you want to create (input, output, processor)",
                        default="processor")

    args = parser.parse_args()

    tpg = TemplateParser(os.path.join(util.get_ax_root(), 'templates'))
    tpg.parse_template('Node.tpl')
