#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.cli.generator import TemplateParser
import atraxiflow.core.util as util
import os


def test_basic():
    tpg = TemplateParser(os.path.join(util.get_ax_root(), 'templates'))
    assert tpg.parse_template('Node.tpl', True) is not None
