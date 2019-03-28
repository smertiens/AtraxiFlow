#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.nodes.common import ExecNode
from atraxiflow.core.stream import *


def test_basic(capsys):
    def callback():
        print('Hello callback!')
        return 'done'

    st = Stream()
    ex = ExecNode({'callable': callback})
    st >> ex

    assert st.flow()
    assert ex.get_output() == 'done'

    captured = capsys.readouterr()
    assert captured[0] == 'Hello callback!\n'