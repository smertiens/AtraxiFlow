#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from atraxiflow.base.filesystem import LoadFilesNode
from atraxiflow.core import *

import os


def test_node(tmpdir):
    tmpdir = str(tmpdir)

    p1 = os.path.join(tmpdir, 'dir1')
    p2 = os.path.join(tmpdir, 'dir2')
    p3 = os.path.join(tmpdir, '*')

    os.makedirs(p1)
    os.makedirs(p2)

    node = LoadFilesNode({
        'paths': [p1, p2, p3]
    })

    Workflow.create([node]).run()

    assert node.get_output().size() == 4


