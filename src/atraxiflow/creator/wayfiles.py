#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import importlib
import json
import logging
import uuid
from typing import List, Any

import re
from PySide2 import QtCore
from atraxiflow import util
from atraxiflow.core import Workflow, Node, MissingRequiredValue
from atraxiflow.creator.widgets import AxNodeWidget

__all__ = ['WayfileException', 'dump', 'load', 'load_as_widgets', 'dump_widgets']

WAYFILE_VERSION = 1, 0, 0


class WayfileException(Exception):
    pass


class WayJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == type(re.compile('')):
            return '__@axflow_internal', 'regex', o.pattern
        elif isinstance(o, MissingRequiredValue):
            return '__@axflow_internal', 'class', 'atraxiflow.core.MissingRequiredValue'

        return json.JSONEncoder.default(self, o)


def _way_unpickle_object(o):
    if isinstance(o, list) and len(o) > 0:
        if o[0] == '__@axflow_internal':
            if o[1] == 'regex':
                return re.compile(o[2])
            elif o[1] == 'class':
                if o[2] == 'atraxiflow.core.MissingRequiredValue':
                    return MissingRequiredValue()

            raise WayfileException('Cannot decode internal axflow object %s' % o)

    return o


def _get_data_skeleton() -> dict:
    data = {
        'file_version': WAYFILE_VERSION,
        'meta': {
            'author': '',
            'comment': ''
        },
        'nodes': [],
        'creator': {
            'ui_nodes': []
        }
    }

    return data


def _build_data_from_node(ax_node: Node, ui_node_id) -> dict:
    return {
        'ui_node': ui_node_id,
        'node_class': ax_node.__class__.__module__ + '.' + ax_node.__class__.__name__,
        'properties': ax_node.serialize_properties(),
    }


def dump(filename: str, nodes: List[Node]):
    data = _get_data_skeleton()

    for node in nodes:
        node.apply_ui_data()

        node_data = _build_data_from_node(node, '')
        data['nodes'].append(node_data)

    logging.getLogger('creator').debug('Saving workflow to file %s' % filename)
    with open(filename, 'w') as f:
        json.dump(data, f, cls=WayJSONEncoder)


def dump_widgets(filename: str, node_widgets: List[AxNodeWidget]):
    data = _get_data_skeleton()

    node_ids = {}
    for node in node_widgets:
        node_ids[node] = str(uuid.uuid4())

    for node in node_widgets:
        ax_node = node.get_node()
        ax_node.apply_ui_data()

        parent_widget_id = None
        if node.dock_parent_widget is not None:
            parent_widget_id = node_ids[node.dock_parent_widget]

        child_widget_id = None
        if node.dock_child_widget is not None:
            child_widget_id = node_ids[node.dock_child_widget]

        node_data = _build_data_from_node(ax_node, node_ids[node])

        ui_node_data = {
            'id': node_ids[node],
            'pos': (node.pos().x(), node.pos().y()),
            'parent_widget': parent_widget_id,
            'child_widget': child_widget_id
        }

        data['nodes'].append(node_data)
        data['creator']['ui_nodes'].append(ui_node_data)

    logging.getLogger('creator').debug('Saving workflow to file %s' % filename)
    with open(filename, 'w') as f:
        json.dump(data, f, cls=WayJSONEncoder)


def _open_and_validate(filename: str) -> Any:
    logging.getLogger('creator').debug('Loading workflow from file %s' % filename)
    with open(filename, 'r') as f:
        data = json.load(f)

    # Check version before loading
    running_ver = util.version_tuple_to_int(WAYFILE_VERSION)
    file_ver = util.version_tuple_to_int(data['file_version'])

    if file_ver > running_ver:
        raise WayfileException('Cannot load file, requires Wayfile library version %s' % util.version_tuple_to_str(data['file_version']))

    return data


def load(filename: str) -> list:
    nodes = []
    data = _open_and_validate(filename)
    for raw_node in data['nodes']:
        node_inst = _create_and_setup_nodes_from_raw_data(raw_node)
        nodes.append(node_inst)

    return nodes


def _create_and_setup_nodes_from_raw_data(raw_node: dict) -> Node:
    mod = raw_node['node_class'][:raw_node['node_class'].rfind('.')]
    node_class = raw_node['node_class'][raw_node['node_class'].rfind('.') + 1:]

    imp_mod = importlib.import_module(mod)
    if hasattr(imp_mod, node_class):
        node_mem = getattr(imp_mod, node_class)
        node_inst = node_mem()
    else:
        raise WayfileException('Could not find node class: %s.%s' % (mod, node_class))

    for name, val in raw_node['properties'].items():
        node_inst.property(name).set_value(_way_unpickle_object(val))

    return node_inst


def load_as_widgets(filename: str) -> List[AxNodeWidget]:
    nodes = []
    ui_nodes = []
    data = _open_and_validate(filename)

    # Since AxNodeWidgets must reference other widgets for docking, we map the node ids of our file
    # to the resulting widgets and assign the correct widget references later
    node_ids = {}

    # Recreate nodes
    for raw_ui_node in data['creator']['ui_nodes']:
        node_inst = None
        for raw_node in data['nodes']:
            if raw_node['ui_node'] == raw_ui_node['id']:
                node_inst = _create_and_setup_nodes_from_raw_data(raw_node)

        if node_inst is None:
            raise WayfileException('Could not find corresponding node for ui id %s' % raw_ui_node['id'])

        widget = AxNodeWidget(node_inst)
        node_inst.load_ui_data()
        setattr(widget, '_tmp_child', raw_ui_node['child_widget'])
        setattr(widget, '_tmp_parent', raw_ui_node['parent_widget'])
        widget.move(QtCore.QPoint(raw_ui_node['pos'][0], raw_ui_node['pos'][1]))

        node_ids[raw_ui_node['id']] = widget
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
