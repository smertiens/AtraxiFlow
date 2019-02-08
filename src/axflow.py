import argparse
import NodeManager
import json
from nodes import Node, InputNode, ProcessorNode, OutputNode
from resources import  Resource

def dump_nodes(outputfile, format):
    nm = NodeManager.NodeManager()
    nodes = nm.findAvailableNodes()
    data = {"nodes": []}

    for node in nodes:
        n = node()
        props = []
        nodeType = ""

        for name, opts in n.getKnownProperties().items():
            opts['name'] = name
            props.append(opts)

        if issubclass(node, InputNode.InputNode):
            nodeType = 'input'
        elif issubclass(node, OutputNode.OutputNode):
            nodeType = 'output'
        elif issubclass(node, ProcessorNode.ProcessorNode):
            nodeType = 'processor'
        elif issubclass(node, Resource.Resource):
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
                        help='an integer for the accumulator', default="run")
    parser.add_argument("--save-to", type=str, help="Data produced by dump-nodes will be saved to this file",
                        default="./nodes.json")
    parser.add_argument("--export-format", type=str, help="The format to which dump-nodes will output the node data "
                        "to.  At the moment only 'json' is supported.", default="json")

    args = parser.parse_args()

    if args.command == "dump-nodes":
        dump_nodes(args.save_to, args.export_format)

