from http.server import BaseHTTPRequestHandler
import json
import cgi
from urllib import parse
from http.server import HTTPServer
import actions
from settings import API_KEY, IGNORE_AUTH


class JobQueueHandler(BaseHTTPRequestHandler):
    get_actions = {
        "/status": actions.status,
    }

    post_actions = {
        "/add-task": actions.add_task,
        "/upload-job": actions.upload_job
    }

    actions = {
        'GET': get_actions,
        'POST': post_actions
    }

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        action = self.get_action('GET')
        if not self.is_authorized():
            self.error_401()
        elif action:
            try:
                resp = bytes(json.dumps(action(self)), 'UTF-8')
                self.send_response(200)
                self.send_headers()
                self.wfile.write(resp)
            except Exception:
                self.error_500()
        else:
            self.error_400()

    def do_POST(self):
        action = self.get_action('POST')
        if not self.is_authorized():
            self.error_401()
        elif action:
            try:
                resp = bytes(json.dumps(action(self)), 'UTF-8')
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

    def is_authorized(self):
        auth = self.headers["authorization"]
        return (auth == API_KEY) or IGNORE_AUTH

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

    def error_401(self):
        self.send_response(401)
        self.wfile.write(bytes("Need to be authroized", "UTF-8"))


class WorkerServer(HTTPServer):

    def __init__(self, server_address, manager, bind_and_activate=True):
        super().__init__(server_address, JobQueueHandler, bind_and_activate)
        self.manager = manager

    def teardown(self):
        self.manager.shutdown()
        self.socket.close()

    def start(self, poll_interval=0.5):
        if not self.manager.are_workers_active():
            self.manager.init_workers()
        self.serve_forever(poll_interval)