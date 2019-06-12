#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.base.common import *
from atraxiflow.base.filesystem import LoadFilesNode

def test_add_nodes():
    wf = Workflow()
    assert wf._nodes == []
    test = NullNode()
    wf.add_node(test)
    assert wf._nodes == [test]

def test_run_workflow():
    node = LoadFilesNode({'path': './*'})
    Workflow.create([node, EchoOutputNode()]).run()

