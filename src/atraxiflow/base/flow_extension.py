#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
"""
This is AtraxiFlow's base extension.
"""
from atraxiflow.core import *


def boot(ctx: WorkflowContext):
    ctx.publish_nodes('AtraxiFlow', {
        'Common': ctx.autodiscover_nodes('atraxiflow.base.common'),
        'Filesystem': ctx.autodiscover_nodes('atraxiflow.base.filesystem'),
        'Text': ctx.autodiscover_nodes('atraxiflow.base.text')
    })
