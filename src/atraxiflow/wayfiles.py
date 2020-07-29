#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019 - 2020 Sean Mertiens
# For more information on licensing see LICENSE file
#

import importlib
import json
import logging
import re
import uuid
from typing import Any

from atraxiflow import util
from atraxiflow.core import Node, MissingRequiredValue

__all__ = ['WayfileException', 'Wayfile', 'WayNode', 'WayWorkflow', 'WayDefaultWorkflow']


class WayfileException(Exception):
    pass


class WayNode:

    def __init__(self, node: Node, data=None):
        if data is None:
            data = {}

        self.node_data = self._build_data_from_node(node, data)

        self.node = node
        self.data = data

    def _build_data_from_node(self, ax_node: Node, data: dict) -> dict:
        return {
            'creator:id': data['creator_id'] if 'creator_id' in data else None,
            'creator:pos': data['creator_pos'] if 'creator_pos' in data else None,
            'creator:parent': data['creator_parent'] if 'creator_parent' in data else None,
            'creator:child': data['creator_child'] if 'creator_child' in data else None,
            'node_class': ax_node.__class__.__module__ + '.' + ax_node.__class__.__name__,
            'properties': ax_node.serialize_properties(),
        }


class WayWorkflow:

    def __init__(self, name: str, data: dict = None):
        self.name = name
        self.nodes = []

        if data is None:
            data = {}

        self.data = data

    def add_node(self, node: WayNode):
        self.nodes.append(node)

    def get_nodes(self) -> list:
        return self.nodes

    def get_name(self):
        return self.name


class WayDefaultWorkflow(WayWorkflow):
    pass


class Wayfile:
    WAYFILE_VERSION = 1, 0, 0

    def __init__(self):
        self.workflows = []

    def _reset(self):
        self.workflows = []

    def load(self, filename: str):

        self._reset()
        data = self._open_and_validate(filename)

        # load workflows
        for wf_id, workflow in data['workflows'].items():

            data = {}

            if 'creator:pos' in workflow:
                data['creator_pos'] = workflow['creator:pos']

            if wf_id == '@default':
                wf = WayDefaultWorkflow(workflow['name'], data)
            else:
                wf = WayWorkflow(workflow['name'], data)

            # load nodes
            for raw_node in workflow['nodes']:
                node_inst = self._create_and_setup_nodes_from_raw_data(raw_node)
                way_node = WayNode(node_inst, {
                    'creator_id': raw_node['creator:id'] if 'creator:id' in raw_node else None,
                    'creator_parent': raw_node['creator:parent'] if 'creator:parent' in raw_node else None,
                    'creator_child': raw_node['creator:child'] if 'creator:child' in raw_node else None,
                    'creator_pos': raw_node['creator:pos'] if 'creator:pos' in raw_node else None,
                })
                wf.add_node(way_node)

            self.add_workflow(wf)

    def add_workflow(self, wf: WayWorkflow):
        self.workflows.append(wf)

    def save(self, filename: str):
        data = self._get_data_skeleton()

        for wf in self.workflows:
            data_wf_node = []
            wf_id = str(uuid.uuid4())

            for node in wf.nodes:
                data_wf_node.append(node.node_data)

            if isinstance(wf, WayDefaultWorkflow):
                data['workflows']['@default'] = {'nodes': data_wf_node, 'name': ''}
            else:
                data['workflows'][wf_id] = {
                    'nodes': data_wf_node,
                    'name': wf.name,
                    'creator:pos': wf.data['creator_pos'] if 'creator_pos' in wf.data else None
                }

        logging.getLogger('creator').debug('Saving workflow to file %s' % filename)
        with open(filename, 'w') as f:
            json.dump(data, f, cls=WayJSONEncoder)

    def _get_data_skeleton(self) -> dict:
        data = {
            'file_version': self.WAYFILE_VERSION,
            'meta': {
                'author': '',
                'comment': ''
            },
            'workflows': {
                '@default': {'nodes': [], 'name': ''}
            }
        }

        return data

    def create_node_from_raw_data(self, raw_node: dict) -> Node:
        return self._create_and_setup_nodes_from_raw_data(raw_node)

    def _create_and_setup_nodes_from_raw_data(self, raw_node: dict) -> Node:
        mod = raw_node['node_class'][:raw_node['node_class'].rfind('.')]
        node_class = raw_node['node_class'][raw_node['node_class'].rfind('.') + 1:]

        imp_mod = importlib.import_module(mod)
        if hasattr(imp_mod, node_class):
            node_mem = getattr(imp_mod, node_class)
            node_inst = node_mem()
        else:
            raise WayfileException('Could not find node class: %s.%s' % (mod, node_class))

        for name, val in raw_node['properties'].items():
            node_inst.property(name).set_value(self._way_unpickle_object(val))

        return node_inst

    def _open_and_validate(self, filename: str) -> Any:
        logging.getLogger('creator').debug('Loading workflow from file %s' % filename)
        with open(filename, 'r') as f:
            data = json.load(f)

        # Check version before loading
        running_ver = util.version_tuple_to_int(self.WAYFILE_VERSION)
        file_ver = util.version_tuple_to_int(data['file_version'])

        if file_ver > running_ver:
            raise WayfileException(
                'Cannot load file, requires Wayfile library version %s' % util.version_tuple_to_str(
                    data['file_version']))

        return data

    def _way_unpickle_object(self, o):
        if isinstance(o, list) and len(o) > 0:
            if o[0] == '__@axflow_internal':
                if o[1] == 'regex':
                    return re.compile(o[2])
                elif o[1] == 'class':
                    if o[2] == 'atraxiflow.core.MissingRequiredValue':
                        return MissingRequiredValue()

                raise WayfileException('Cannot decode internal axflow object %s' % o)

        return o


class WayJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == type(re.compile('')):
            return '__@axflow_internal', 'regex', o.pattern
        elif isinstance(o, MissingRequiredValue):
            return '__@axflow_internal', 'class', 'atraxiflow.core.MissingRequiredValue'

        return json.JSONEncoder.default(self, o)
