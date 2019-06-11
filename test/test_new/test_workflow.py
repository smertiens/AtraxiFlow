#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.nodes.filesystem import *

def test_add_nodes():
    pass

def test_run_workflow():
    node = LoadFilesNode({'path': './*'})
    Workflow.create([node]).run()

    print(node.get_output().items()[0])
