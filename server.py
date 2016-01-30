from http.server import BaseHTTPRequestHandler
import json
import cgi
from urllib import parse
from http.server import HTTPServer
import actions


class JobQueueHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.actions = server.actions
        super().__init__(request, client_address, server)

    def do_GET(self):
        action = self.get_action('GET')
        if action:
            try:
                resp = bytes(json.dumps(action(self.path)), 'UTF-8')
                self.send_response(200)
                self.send_headers()
                self.wfile.write(resp)
            except Exception:
                self.error_500()
        else:
            self.error_400()

    def do_POST(self):
        action = self.get_action('POST')
        post_data = self.get_post_data()
        if action:
            try:
                resp = bytes(json.dumps(action(self.path, post_data)), 'UTF-8')
                self.send_response(200)
                self.send_headers()
                self.wfile.write(resp)
            except Exception:
                self.error_500()
        else:
            self.error_400()

    def get_action(self, method):
        _actions = self.actions.get(method)
        if _actions:
            if '?' in self.path:
                return _actions.get(self.path.split('?')[0])
            return _actions.get(self.path)
        return None

    def get_post_data(self):
        content_type, parts_dict = cgi.parse_header(self.headers["content-type"])
        if content_type == "multipart/form-data":
            parts_dict["boundary"] = bytes(parts_dict["boundary"], "UTF-8")
            params = cgi.parse_multipart(self.rfile, parts_dict)
        elif content_type == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            params = parse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            params = {}
        return self.fix_post_params(params)

    def fix_post_params(self, params):
        ret = {}
        for key in params:
            ret[key.decode("utf-8") if isinstance(key, bytes) else key] = [val.decode("utf-8") for val in params[key]]
        return ret

    def send_headers(self):
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def error_500(self):
        self.send_response(500)
        self.wfile.write(bytes("Uh Oh Something Went Wrong....", "UTF-8"))

    def error_400(self):
        print(self.actions)
        self.send_response(400)
        self.wfile.write(bytes("Invalid Request", "UTF-8"))


class WorkerServer(HTTPServer):

    def __init__(self, server_address, manager, bind_and_activate=True):
        super().__init__(server_address, JobQueueHandler, bind_and_activate)
        self.manager = manager
        self.get_actions = {
            "/status": actions.status(self.manager),
        }

        self.post_actions = {
            "/add-task": actions.add_task(self.manager),
            "/upload-job": actions.upload_job
        }

        self.actions = {
            'GET': self.get_actions,
            'POST': self.post_actions
        }

    def teardown(self):
        self.manager.shutdown()
        self.socket.close()

    def start(self, poll_interval=0.5):
        if not self.manager.are_workers_active():
            self.manager.init_workers()
        self.serve_forever(poll_interval)