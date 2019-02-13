#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import importlib
import pkgutil

from atraxiflow.nodes.foundation import Node as baseNode
from atraxiflow.nodes.foundation import Resource as baseResource


class NodeManager:

    # TODO: needs to be rewritten considering the package changes
    def find_available_nodes(self, include_resources=True):

        # find Nodes
        found_nodes = []
        ignore = ['foundation']

        for importer, modname, ispkg in pkgutil.iter_modules(nodes.__path__):
            if not ispkg and modname not in ignore:
                module = importlib.import_module("nodes." + modname)
                cls = getattr(module, modname)

                if issubclass(cls, baseNode):
                    found_nodes.append(cls)

        # find Resources
        if include_resources is True:
            import resources

            ignore = ['Resource']

            for importer, modname, ispkg in pkgutil.iter_modules(resources.__path__):
                if not ispkg and modname not in ignore:
                    module = importlib.import_module("resources." + modname)
                    cls = getattr(module, modname)

                    if issubclass(cls, baseResource):
                        found_nodes.append(cls)

        return found_nodes
