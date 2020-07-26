#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019 - 2020 Sean Mertiens
# For more information on licensing see LICENSE file
#

import http.server

class RequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.log_request()

class CreatorServer:

    port = 8000

    def __init__(self):
        pass

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