import io, logging, sys
from threading import Thread

from atraxiflow.core import WorkflowContext, Workflow
from atraxiflow.core import Node, MissingRequiredValue
from atraxiflow.properties import Property
from atraxiflow.wayfiles import Wayfile
from atraxiflow.axlogging import AxLoggingListHandler

class WorkflowThread(Thread):

    _stdout_buf = None
    _stderr_buf = None
    _nodes = []
    _log_handler = None
    _running = False

    def __init__(self):
        super().__init__()

        self._stdout_buf = io.StringIO()
        self._stderr_buf = io.StringIO()
        self._log_handler = AxLoggingListHandler(logging.DEBUG)
        self._running = False

    def set_nodes(self, nodes):
        self._nodes = nodes

    def get_log_records(self):
        return self._log_handler.get_records()

    def get_stdout_buffer(self):
        return self._stdout_buf

    def get_stderr_buffer(self):
        return self._stderr_buf

    def is_running(self):
        return self._running

    def run(self):

        wf = Workflow()
        f = Wayfile()

        for node in self._nodes:
            wf.add_node(f.create_node_from_raw_data(node))

        logging.getLogger('core').addHandler(self._log_handler)
        logging.getLogger('workflow_ctx').addHandler(self._log_handler)

        sys.stdout = self._stdout_buf
        sys.stderr = self._stderr_buf
        
        self._running = True
        wf.run()
        self._running = False

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self._stdout_buf.seek(0)
        self._stderr_buf.seek(0)

        logging.getLogger('core').removeHandler(self._log_handler)
        logging.getLogger('workflow_ctx').removeHandler(self._log_handler)