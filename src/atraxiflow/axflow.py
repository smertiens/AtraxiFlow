#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import argparse
import atraxiflow.NodeManager
import json, os
from atraxiflow.nodes.foundation import InputNode, ProcessorNode, OutputNode, Resource

def create_from_template(tpl, name, tp):
    parentNode = ""
    if (tp == 'input'):
        parentNode = 'InputNode'
    elif (tp == 'output'):
        parentNode = 'OutputNode'
    else:
        parentNode = 'ProcessorNode'

    base_path = os.path.dirname(os.path.realpath(__file__));

    if tpl == 'node':
        tpl_path = os.path.join(base_path, 'templates', 'Node.tpl')
    elif tpl == 'resource':
        tpl_path = os.path.join(base_path, 'templates', 'Resource.tpl')
    elif tpl == 'script':
        tpl_path = os.path.join(base_path, 'templates', 'Script.tpl')
    else:
        print("Error: Invalid template '{0}'".format(tpl))
        return False

    fp = open(tpl_path, 'r')
    content = fp.read()
    fp.close()

    replace_map = {
        '{# ClassName #}' : name,
        '{# Type #}' : parentNode
    }

    for search, replace in replace_map.items():
        content = content.replace(search, replace)

    fp = open(os.path.join(base_path, 'nodes', name + '.py'), 'w')
    fp.write(content)
    fp.close()

    print ("Created file {0} in nodes".format(name + '.py'))


def dump_nodes(outputfile, format):
    nm = NodeManager.NodeManager()
    nodes = nm.find_available_nodes()
    data = {"nodes": []}

    for node in nodes:
        n = node()
        props = []
        nodeType = ""

        for name, opts in n.get_known_properties().items():
            opts['name'] = name
            props.append(opts)

        if issubclass(node, InputNode):
            nodeType = 'input'
        elif issubclass(node, OutputNode):
            nodeType = 'output'
        elif issubclass(node, ProcessorNode):
            nodeType = 'processor'
        elif issubclass(node, Resource):
            nodeType = 'resource'

        data['nodes'].append({
            'nodeClass': n.__class__.__name__,
            'nodeType': nodeType,
            'props': props
        })

    fp = open(outputfile, "w+")

    if format == "json":
        json.dump(data, fp)

    fp.close()


if __name__ == '__main__':

    # Parse CLI args
    parser = argparse.ArgumentParser(description="Flow based workflow tool")

    parser.add_argument('command', metavar='cmd', type=str, nargs='?',
                        help='The command you want to execute')

    ### create:node ###
    parser.add_argument("--name", type=str, help="The class name of the node you want to create",
                        default="NewNode")
    parser.add_argument("--node-type", type=str, help="The node type you want to create (input, output, processor)",
                        default="processor")

    ### dump:nodes ###
    parser.add_argument("--save-to", type=str, help="Data produced by dump-nodes will be saved to this file",
                        default="./nodes.json")
    parser.add_argument("--export-format", type=str, help="The format to which dump-nodes will output the node data "
                        "to.  At the moment only 'json' is supported.", default="json")

    args = parser.parse_args()

    if args.command == "dump:nodes":
        dump_nodes(args.save_to, args.export_format)
    elif args.command == "create:node":
        create_from_template('node', args.name, args.node_type)
    elif args.command == "create:resource":
        create_from_template('resource', args.name, args.node_type)


