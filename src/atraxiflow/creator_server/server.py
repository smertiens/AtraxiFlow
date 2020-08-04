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

from atraxiflow.creator_server import runner
from atraxiflow.core import WorkflowContext, Workflow
from atraxiflow.core import Node, MissingRequiredValue
from atraxiflow.properties import Property
from atraxiflow import wayfiles

server_state = {
    'port': 8000,
    'cors_port': 8000,
    'orig_cwd': '',
    'current_wf_thread': None
}

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
        '/axflow/execstatus': 'execution_status',
        '/axflow/filebrowser': 'filebrowser',
        '/axflow/ping': 'ping',
        '/axflow/save': 'save_file'
    }

    request = Request()

    def ping(self):
        self.send_json_response(json.dumps({
            'status': 'ok'
        }))

    def save_file(self):
        data = None

        try:
            data = json.loads(self.request.content)
        except json.JSONDecodeError:
            self.send_json_response(json.dumps({
                'status': 'error',
                'msg': 'Corrupted data'
            }))
            return

        nodes = data['data']
        relpath = os.path.join(data['file']['path'], data['file']['filename']).lstrip(os.path.sep)
        savepath = os.path.realpath(os.path.join(server_state['orig_cwd'], relpath))

        if savepath == '':
            self.send_json_response(json.dumps({
                'status': 'error',
                'msg': 'Invalid directory'
            }))
            return
        
        way = wayfiles.Wayfile()

        wf_nodes = []

        for id, node in nodes.items():
            if node['node_class'] == '@Workflow':
                wf_nodes.append(node)
        
        for wf_node in wf_nodes:
            wf = wayfiles.WayWorkflow(wf_node['creator_label'], {
                'creator_id': wf_node['creator_id'],
                'creator_pos': wf_node['creator_pos']
            })

            if wf_node['creator_child'] is not None:
                self._add_wf_nodes_recursive(wf, nodes[wf_node['creator_child']], nodes)

            way.add_workflow(wf)
        
        way.save(savepath)

        self.send_json_response(json.dumps({
            'status': 'ok'
        }))

    def _add_wf_nodes_recursive(self, wf: wayfiles.WayWorkflow, node: dict, nodes):
        wf.add_node(wayfiles.WayNode.create_from_array(node))

        if node['creator_child'] is not None:
            self._add_wf_nodes_recursive(wf, nodes[node['creator_child']], nodes)

    def filebrowser(self):
        path = '' if 'path' not in self.request.query else self.request.query['path'].strip('/\\')
        filter = '' if 'filter' not in self.request.query else self.request.query['filter']
        
        # files will be accessible starting from the directory creator was started in
        local_path = os.path.realpath(os.path.join(server_state['orig_cwd'], path))
        filtered_dirs = []
        
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
        
        server_state['current_wf_thread'] = runner.WorkflowThread()
        server_state['current_wf_thread'].set_nodes(nodes)
        server_state['current_wf_thread'].start()

        self.send_json_response(json.dumps({
            'status': 'ok',
        }))

    def execution_status(self):
        data = {}

        if server_state['current_wf_thread'] == None:
            data = {
                'status': 'not_started',
                'messages': [],
                'stdout': [],
                'stderr': []
            }
        else:
            data = {
                'status': 'running' if server_state['current_wf_thread'].is_running() else 'done',
                'messages': server_state['current_wf_thread'].get_log_records(),
                'stdout': server_state['current_wf_thread'].get_stdout_buffer().readlines(),
                'stderr': server_state['current_wf_thread'].get_stderr_buffer().readlines()
            }

        self.send_json_response(json.dumps(data))
        

    def node_list(self):
        wfc = WorkflowContext()
        nodes = json.dumps(wfc.get_nodes(), cls=NodeJSONEncoder)
        self.send_json_response(nodes)

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:%s' % server_state['cors_port'])
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
            # try to serve from directory
            return super().do_GET()

        else:
            a = getattr(self, self.routes[self.request.path])
            a()

    def do_OPTIONS(self):
        # TODO: Review correct CORS protocal usage - works for now
        # see here: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Preflighted_requests
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:%s' % server_state['cors_port'])
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.log_request()

    def do_GET(self):
        self._handle_request()
        self.log_request()

    def do_POST(self):
        self._handle_request()
        self.log_request()
        
class CreatorServer:

    port = 8000
    creator_path = ''

    def __init__(self, port = 8000, cors_port = None):
        self.port = port
        server_state['cors_port'] = cors_port if cors_port is not None else self.port

    def start(self):
        try:
            from atraxicreator import WEB_PATH
            
            if not os.path.exists(WEB_PATH):
                logging.getLogger('core').error('Creator web path is invalid.')
                sys.exit(1)

            server_state['orig_cwd'] = os.getcwd()
            os.chdir(WEB_PATH)

        except ImportError:
            logging.getLogger('core').error('Could not find AtraxiCreator installation. ' +
                            'Install it with pip3 install atraxi-creator-web.')
            sys.exit(1)
            
        srv = http.server.HTTPServer(('', self.port), RequestHandler)
        print("Started server on http://localhost:%s" % (self.port))

        server_state['port'] = self.port
        
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("Goodbye.")

        if server_state['orig_cwd'] != '':
            os.chdir(server_state['orig_cwd'])
