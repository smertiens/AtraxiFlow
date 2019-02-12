#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import time

from nodes.foundation import ProcessorNode


class DelayNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'time' : {
                'required': False,
                'hint': 'Delay time in seconds',
                'default': '5'
            }
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def run(self, stream):
        self.check_properties()

        time.sleep(int(self.get_property('time')))

        return True
