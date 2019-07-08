#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pickle, uuid, logging
import importlib
from typing import List
from atraxiflow import __version__
from atraxiflow.creator.widgets import AxNodeWidget
from PySide2 import QtCore


def dump(filename: str, node_widgets: List[AxNodeWidget]):
    data = {
        'ax_version': __version__,
        'nodes': []
    }

    node_ids = {}
    for node in node_widgets:
        node_ids[node] = str(uuid.uuid4())

    for node in node_widgets:
        ax_node = node.get_node()

        parent_widget = None
        if node.dock_parent_widget is not None:
            parent_widget = node_ids[node.dock_parent_widget]

        child_widget = None
        if node.dock_child_widget is not None:
            child_widget = node_ids[node.dock_child_widget]

        node_data = {
            'id': node_ids[node],
            'pos': (node.pos().x(), node.pos().y()),
            'ax_node_class': ax_node.__class__.__module__ + '.' + ax_node.__class__.__name__,
            'ax_node': ax_node.serialize(),
            'parent_widget': parent_widget,
            'child_widget': child_widget
        }

        data['nodes'].append(node_data)

    logging.getLogger('creator').debug('Saving workflow to file {}'.format(filename))
    with open(filename, 'bw') as f:
        pickle.dump(data, f)


def load(filename: str) -> List[AxNodeWidget]:
    nodes = []

    logging.getLogger('creator').debug('Loading workflow from file {}'.format(filename))
    with open(filename, 'br') as f:
        data = pickle.load(f)

    # TODO: check version

    for raw_node in data['nodes']:
        mod = raw_node['ax_node_class'][:raw_node['ax_node_class'].rfind('.')]
        node_class = raw_node['ax_node_class'][raw_node['ax_node_class'].rfind('.') + 1:]

        imp_mod = importlib.import_module(mod)
        if hasattr(imp_mod, node_class):
            node_mem = getattr(imp_mod, node_class)
            node_inst = node_mem()
        else:
            raise Exception('Could not find node class')

        for name, val in raw_node['ax_node'].items():
            node_inst.property(name).set_value(val)

        widget = AxNodeWidget(node_inst)
        widget.move(QtCore.QPoint(raw_node['pos'][0],raw_node['pos'][1]))

        nodes.append(widget)

    return nodes
