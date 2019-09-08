#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

from atraxiflow.base.filesystem import *


def test_change_cwd(tmpdir):
    old = os.getcwd()

    Workflow.create([FSChangeCWDNode({'cwd': str(tmpdir)})]).run()

    assert old != os.getcwd()
    assert os.getcwd() == str(tmpdir)
