#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.debug import *
from atraxiflow.nodes.common import *


def test_debug_print_resources(capsys):
    st = Stream()
    st.add_resource(TextResource('text1', {'text': 'Hello'}))
    st.add_resource(TextResource('text2', {'text': 'World'}))

    Debug.print_resources(st, '*')

    captured = capsys.readouterr()
    assert captured[0] == '1. TextResource (text1) -> data:\n\tstr: Hello\n' \
                          '2. TextResource (text2) -> data:\n\tstr: World\n'
