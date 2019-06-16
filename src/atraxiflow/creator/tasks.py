#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import threading
from atraxiflow.core import *
from typing import List


class RunWorkflowTask(threading.Thread):

    def __init__(self, nodes: List[Node]):
        super().__init__()
        self.nodes = nodes

    def run(self) -> None:
        print('Starting runner tastk')

        wf = Workflow(self.nodes)
        wf.run()
