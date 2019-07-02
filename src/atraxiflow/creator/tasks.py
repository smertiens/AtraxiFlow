#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import threading, logging
from typing import List, Callable

from atraxiflow.core import *


class Task(threading.Thread):
    def __init__(self):
        super().__init__()

        self.on_start = None
        self.on_finish = None
        self.on_status_msg_changed = None

    def set_on_start(self, c: Callable):
        self.on_start = c

    def set_on_finish(self, c: Callable):
        self.on_finish = c

    def set_on_status_msg_changed(self, c: Callable):
        self.on_status_msg_changed = c

    def emit_on_start(self):
        if self.on_start is not None:
            self.on_start(self)

    def emit_on_finish(self):
        if self.on_finish is not None:
            self.on_finish(self)

    def emit_on_status_msg_changed(self, msg: str):
        if self.on_status_msg_changed is not None:
            self.on_status_msg_changed(msg)


class RunWorkflowTask(Task):

    def __init__(self, nodes: List[Node]):
        super().__init__()
        self.nodes = nodes
        self.workflow = Workflow(nodes)

    def get_workflow(self):
        return self.workflow

    def run(self) -> None:
        self.emit_on_start()
        self.emit_on_status_msg_changed('Starting workflow...')

        self.workflow.run()

        self.emit_on_finish()
