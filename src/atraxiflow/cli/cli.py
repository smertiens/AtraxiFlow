#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import json
import os

from atraxiflow.core.nodemanager import NodeManager
from atraxiflow.nodes.foundation import InputNode, ProcessorNode, OutputNode, Resource


def create_from_template(tpl, name, tp):
    parentNode = ""
    if tp == 'input':
        parentNode = 'InputNode'
    elif tp == 'output':
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
        '{# ClassName #}': name,
        '{# Type #}': parentNode
    }

    for search, replace in replace_map.items():
        content = content.replace(search, replace)

    fp = open(os.path.join(base_path, 'nodes', name + '.py'), 'w')
    fp.write(content)
    fp.close()

    print("Created file {0} in nodes".format(name + '.py'))


def dump_nodes(outputfile, format):
    nm = NodeManager()
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
