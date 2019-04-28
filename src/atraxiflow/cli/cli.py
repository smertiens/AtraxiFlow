#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os
from atraxiflow.cli.generator import TemplateParser
import atraxiflow.core.util as util
from atraxiflow.core.nodemanager import NodeManager
from atraxiflow.nodes.foundation import *


def create_from_template(tpl, name, tp):

    tpg = TemplateParser(os.path.join(util.get_ax_root(), 'templates'))
    tpg._parse_template('Node.tpl')

    return
    parentNode = ""
    if tp == 'input':
        parentNode = 'InputNode'
    elif tp == 'output':
        parentNode = 'OutputNode'
    else:
        parentNode = 'ProcessorNode'

    base_path = os.path.dirname(os.path.realpath(os.path.join(__file__, "..")));

    if tpl == 'node':
        tpl_path = os.path.join(base_path, 'templates', 'Node.tpl')
    elif tpl == 'resource':
        tpl_path = os.path.join(base_path, 'templates', 'Resource.tpl')
    elif tpl == 'script':
        tpl_path = os.path.join(base_path, 'templates', 'Script.tpl')
    else:
        print("Error: Invalid template '{0}'".format(tpl))
        return False

    fp = open(tpl_path, 'r')
    content = fp.read()
    fp.close()

    replace_map = {
        '{# ClassName #}': name,
        '{# Type #}': parentNode
    }

    content = content.maketrans(replace_map)

    fp = open(os.path.join(base_path, 'nodes', name + '.py'), 'w')
    fp.write(content)
    fp.close()

    print("Created file {0} in nodes".format(name + '.py'))


def list_entities(filter=None):
    pass
