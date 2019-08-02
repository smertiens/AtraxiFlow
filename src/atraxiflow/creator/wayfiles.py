#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
# TODO: Implement tests for wayfiles

import importlib
import logging
import pickle
import uuid
from typing import List, Any

from PySide2 import QtCore
from atraxiflow import __version__, util
from atraxiflow.core import Workflow, Node
from atraxiflow.creator.widgets import AxNodeWidget

__all__ = ['WayfileException', 'dump', 'load_as_workflow', 'load']


class WayfileException(Exception):
    pass


def dump(filename: str, node_widgets: List[AxNodeWidget]):
    data = {
        'ax_version': __version__,
        'nodes': []
    }

    node_ids = {}
    for node in node_widgets:
        node_ids[node] = uuid.uuid4().bytes

    for node in node_widgets:
        ax_node = node.get_node()

        parent_widget = None
        if node.dock_parent_widget is not None:
            parent_widget = node_ids[node.dock_parent_widget]

        child_widget = None
        if node.dock_child_widget is not None:
            child_widget = node_ids[node.dock_child_widget]

        ax_node.apply_ui_data()

        node_data = {
            'id': node_ids[node],
            'pos': (node.pos().x(), node.pos().y()),
            'ax_node_class': ax_node.__class__.__module__ + '.' + ax_node.__class__.__name__,
            'ax_node': ax_node.serialize(),
            'parent_widget': parent_widget,
            'child_widget': child_widget
        }

        data['nodes'].append(node_data)

    logging.getLogger('creator').debug('Saving workflow to file %s' % filename)
    with open(filename, 'bw') as f:
        pickle.dump(data, f)


def _open_and_validate(filename: str) -> Any:
    logging.getLogger('creator').debug('Loading workflow from file %s' % filename)
    with open(filename, 'br') as f:
        data = pickle.load(f)

    # Check version before loading
    running_ver = util.version_str_to_int(__version__)
    file_ver = util.version_str_to_int(data['ax_version'])

    if file_ver > running_ver:
        raise WayfileException('Cannot load file, requires AtraxiFlow version %s' % data['ax_version'])

    return data


def load_as_workflow(filename: str) -> Workflow:
    wf = Workflow()
    data = _open_and_validate(filename)
    for raw_node in data['nodes']:
        node_inst = _create_and_setup_nodes_from_raw_data(raw_node)
        wf.add_node(node_inst)

    return wf


def _create_and_setup_nodes_from_raw_data(raw_node: dict) -> Node:
    mod = raw_node['ax_node_class'][:raw_node['ax_node_class'].rfind('.')]
    node_class = raw_node['ax_node_class'][raw_node['ax_node_class'].rfind('.') + 1:]

    imp_mod = importlib.import_module(mod)
    if hasattr(imp_mod, node_class):
        node_mem = getattr(imp_mod, node_class)
        node_inst = node_mem()
    else:
        raise WayfileException('Could not find node class: %s.%s' % (mod, node_class))

    for name, val in raw_node['ax_node'].items():
        node_inst.property(name).set_value(val)

    return node_inst


def load(filename: str) -> List[AxNodeWidget]:
    nodes = []
    data = _open_and_validate(filename)

    # Since AxNodeWidgets must reference other widgets for docking, we map the node ids of our file
    # to the resulting widgets and assign the correct widget references later
    node_ids = {}

    # Recreate nodes
    for raw_node in data['nodes']:
        node_inst = _create_and_setup_nodes_from_raw_data(raw_node)

        widget = AxNodeWidget(node_inst)
        node_inst.load_ui_data()
        setattr(widget, '_tmp_child', raw_node['child_widget'])
        setattr(widget, '_tmp_parent', raw_node['parent_widget'])
        widget.move(QtCore.QPoint(raw_node['pos'][0], raw_node['pos'][1]))

        node_ids[raw_node['id']] = widget
        nodes.append(widget)

    # Dock widgets
    for widget in nodes:
        if widget._tmp_child is not None:
            widget.dock_child_widget = node_ids[widget._tmp_child]
        delattr(widget, '_tmp_child')

        if widget._tmp_parent is not None:
            widget.dock_parent_widget = node_ids[widget._tmp_parent]
        delattr(widget, '_tmp_parent')

    return nodes
