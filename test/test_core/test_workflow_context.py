#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *


def test_symbol_replacement():
    wf = Workflow()

    wf.get_context().set_symbol('demo1', 'Hello World!')
    wf.get_context().set_symbol('demo2', '/23/')

    out = wf.get_context().process_str('I say: {demo1}, demo2')
    assert out == 'I say: Hello World!, demo2'

    out = wf.get_context().process_str('I say: {demo1}, {demo2}')
    assert out == 'I say: Hello World!, /23/'

    out = wf.get_context().process_str('Hello World')
    assert out == 'Hello World'

    # check error logger for message if variable unknown