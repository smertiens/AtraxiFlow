#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.base.common import *
from atraxiflow.base.filesystem import *
from atraxiflow.base.text import *

def test_add_nodes():
    wf = Workflow()
    assert wf._nodes == []
    test = NullNode()
    wf.add_node(test)
    assert wf._nodes == [test]

def test_run_workflow():
    node = LoadFilesNode({'paths': ['./*']})
    Workflow.create([node, EchoOutputNode()]).run()

def test_run_encapsulated_workflows(tmpdir):
    wf_main = Workflow()
    wf_child_1 = Workflow()

    # get text file and delete it
    wf_child_1.add_node(LoadFilesNode({'paths': [str(tmpdir.join('text1'))]}))
    wf_child_1.add_node(FSDeleteNode())

    wf_main.add_node(EchoOutputNode({'msg': 'Test'}))
    wf_main.add_node(TextFileOutputNode({'filename': str(tmpdir.join('text1'))}))
    wf_main.add_workflow(wf_child_1)

    assert wf_main.run()
