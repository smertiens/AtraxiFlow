#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


import argparse

from atraxiflow.cli import cli

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

    if args.command == "create:node":
        cli.create_from_template('node', args.name, args.node_type)
    elif args.command == "create:resource":
        cli.create_from_template('resource', args.name, args.node_type)
