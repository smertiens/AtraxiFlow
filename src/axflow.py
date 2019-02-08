import argparse
import NodeManager
import json

def dump_nodes(outputfile, format):
    nm = NodeManager.NodeManager()
    nodes = nm.findAvailableNodes()
    data = {"nodes": {}}

    for node in nodes:
        n = node()

        data['nodes'][n.getNodeClass()] = {
            'props': n.getKnownProperties()
        }

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

