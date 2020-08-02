#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019 - 2020 Sean Mertiens
# For more information on licensing see LICENSE file
#

import http.server
import json
import inspect
import re, os, logging, sys, io
from urllib.parse import urlparse

from atraxiflow.core import WorkflowContext, Workflow
from atraxiflow.core import Node, MissingRequiredValue
from atraxiflow.properties import Property
from atraxiflow.wayfiles import Wayfile
from atraxiflow.axlogging import AxLoggingListHandler

class NodeJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if inspect.isclass(o):
            
            if (issubclass(o, Node)):
                node = o()
                return {
                    'name': node.id,
                    'properties': node.properties
                }

            else:
                return o.__name__

        elif isinstance(o, Property):
            return o.to_dict()            

        elif type(o) == type(re.compile('')):
            return 're.regex'

        elif isinstance(o, MissingRequiredValue):
            return 'atraxiflow.core.MissingRequiredValue'

        return json.JSONEncoder.default(self, o)

class Request:

    path = ''
    query = {}
    fragment = ''
    content = ''

    def __init__(self, path = '', query_string = '', fragment = '', content = ''):
        self.path = path
        self.fragment = fragment
        self.content = content

        items = query_string.split('&')

        for item in items:
            if item == '':
                continue

            kv = item.split('=')
            self.query[kv[0]] = kv[1]

class RequestHandler(http.server.SimpleHTTPRequestHandler):

    routes = {
        '/axflow/nodes': 'node_list',
        '/axflow/run': 'run_nodes',
        '/axflow/filebrowser': 'filebrowser',
        '/axflow/ping': 'ping'
    }

    request = Request()

    def ping(self):
        self.send_json_response(json.dumps({
            'status': 'ok'
        }))

    def filebrowser(self):
        path = '' if 'path' not in self.request.query else self.request.query['path'].strip('/\\')
        filter = '' if 'filter' not in self.request.query else self.request.query['filter']

        local_path = os.path.realpath(os.path.join(os.getcwd(), path))
        filtered_dirs = []
        
        print(local_path)

        if os.path.exists(local_path):
            dirs = os.listdir(local_path)
            dirs.sort()

            for dir in dirs:
                fullpath = os.path.join(local_path, dir)

                if dir in ('.', '..'): 
                    continue

                if filter == 'dirs':
                    if not os.path.isdir(fullpath):
                        continue
                elif filter == 'files':
                    if os.path.isdir(fullpath):
                        continue
                
                attr = []
                
                if dir.startswith('.'):
                    attr.append('hidden')
                
                if os.path.islink(fullpath):
                    attr.append('link')

                stat = os.stat(fullpath)

                filtered_dirs.append({
                    'name': dir,
                    'type': 'dir' if os.path.isdir(fullpath) else 'file',
                    'attr': attr,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'created': stat.st_ctime
                })

        self.send_json_response(json.dumps({
            'items': filtered_dirs
        }))

    def run_nodes(self):
        nodes = json.loads(self.request.content)
        wf = Workflow()
        f = Wayfile()

        for node in nodes:
            wf.add_node(f.create_node_from_raw_data(node))

        h = AxLoggingListHandler(logging.DEBUG)
        logging.getLogger('core').addHandler(h)
        logging.getLogger('workflow_ctx').addHandler(h)

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        sys.stdout = stdout_buf
        sys.stderr = stdout_buf

        wf.run()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        stdout_buf.seek(0)
        stderr_buf.seek(0)

        logging.getLogger('core').removeHandler(h)
        logging.getLogger('workflow_ctx').removeHandler(h)

        self.send_json_response(json.dumps({
            'status': 'ok',
            'messages': h.get_records(),
            'stdout': stdout_buf.readlines(),
            'stderr': stderr_buf.readlines()
        }))

    def node_list(self):
        wfc = WorkflowContext()
        nodes = json.dumps(wfc.get_nodes(), cls=NodeJSONEncoder)
        self.send_json_response(nodes)

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8080')
        self.end_headers()

        self.wfile.write(bytearray(data, "utf-8"))

    def _handle_request(self):
        frag = urlparse(self.path)

        content = ''

        if 'Content-Length' in self.headers:
            len = int(self.headers['Content-Length'])
            content = self.rfile.read(len)

        self.request = Request(frag.path, frag.query, frag.fragment, content)

        if self.request.path not in self.routes:
            print('No matching route for "%s" found.' % self.request.path)
            self.send_error(404, 'Not found', 'The resource for "%s" could not be found' % self.request.path)
        else:
            a = getattr(self, self.routes[self.request.path])
            a()

    def do_GET(self):
        self._handle_request()
        #self.log_request()

    def do_POST(self):
        self._handle_request()
        #self.log_request()
        
class CreatorServer:

    port = 8000
    creator_path = ''

    def __init__(self, port = 8000):
        self.port = port
        
        try:
            from axcreator.creator import WEB_PATH
            self.creator_path = WEB_PATH
        except ImportError:
            logging.getLogger('core').error('Could not find AtraxiCreator installation. Install it with pip3 install atraxi-creator')
            sys.exit(1)

    def start(self):
        srv = http.server.HTTPServer(('', self.port), RequestHandler)
        print("Started server on http://localhost:%s" % (self.port))
        
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("Exiting.")


if __name__ == "__main__":

    srv = CreatorServer()
    srv.start()    