from nodes.Node import Node as baseNode
import pkgutil, importlib

class NodeManager:

    def findAvailableNodes(self, includeResources = True):

        import nodes
        importlib.import_module("nodes.Node")

        found_nodes = []
        ignore = ['Node', 'ProcessorNode', 'OutputNode', 'InputNode']

        for importer, modname, ispkg in pkgutil.iter_modules(nodes.__path__):
            if not ispkg and modname not in ignore:
                module = importlib.import_module("nodes." + modname)
                cls = getattr(module, modname)

                if issubclass(cls, baseNode):
                    found_nodes.append(cls)


        return found_nodes

