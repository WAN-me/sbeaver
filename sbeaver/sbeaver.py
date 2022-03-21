from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from traceback import print_tb
import urllib.parse
import json
import re

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def __parse_data(datastr: str):
    result = {}
    lines = datastr.split('&')
    for line in lines:
        splited = line.split("=",1)
        key = urllib.parse.unquote(splited[0])
        value = ''
        for word in splited[1].split('+'):
            word = urllib.parse.unquote(word)
            value += word + " "
        value = value[:-1]
        result[key] = value
    return result

class CustomRequest():
    def __init__(self,req: BaseHTTPRequestHandler):
        self.ip = req.client_address[0]
        # parse headers
        self.headers = {}
        for i in range(len(req.headers.values())):
            self.headers[req.headers.keys()[i]] = req.headers.values()[i]

        # parse args
        self.args = {}
        if '?' in req.path:
            splited = req.path.split('?',1)
            self.rawargs = urllib.parse.parse_qs(splited[1])
            self.path = urllib.parse.unquote(splited[0])
            for arg in self.rawargs:
                self.args[arg] = self.rawargs[arg][0]
        else:
            self.path = urllib.parse.unquote(req.path)

        # parse data
        self.data = {}
        length = int(self.headers.get('Content-Length','0'))
        if length > 0:
            self.rawdata = req.rfile.read(length).decode()
            self.data = __parse_data(self.rawdata)

    def __str__(self) -> str:
        return f'headers: {self.headers}\nargs: {self.args}\ndata: {self.data}' 

class CustomHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super(CustomHandler, self).__init__(*args, **kwargs)
    def do_GET(self):
        main_server.async_worker(self)

class Server():
    def bind(self, path_regex=''):
        def my_decorator(func):
            self.bindes[path_regex] = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator

    def ebind(self, path_regex=''):
        """Bind endpoint by '<some>'
        Example: 
        @server.ebind('/ebind/<submethod>/<method>')
        def ebind(request,  submethod = None, method = None):"""
        def my_decorator(func):
            rr = re.findall(r'(<\w+>)+',path_regex)
            reg = path_regex
            for _ in rr:
                if len(_) > 0: 
                    reg = reg.replace(_,r'(\w+)')
            self.bindes[reg] = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
    
    def sbind(self, path):
        """Bind static endpoint on path'
        Example: 
        @server.sbind('/sbind')
        def sbind(request):"""
        def my_decorator(func):
            self.bindes[path+"$"] = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator

    def code404(self):
        def my_decorator(func):
            self.code404 = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
    
    def code500(self):
        def my_decorator(func):
            self.code500 = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
            
    def async_worker(self, request):
        rr = CustomRequest(request)
        try:
            for bind in self.bindes:
                match = re.fullmatch(bind, rr.path)
                if match:
                    res = self.bindes[bind](rr,*match.groups())
                    break
            else:
                res = 404, (self.code404(rr) if self.code404 else {'error':400})
        except Exception as e:
            print_tb(e.__traceback__)
            print(e)
            try:
                res = 500, (self.code500(rr) if self.code500 else {'error':500})
            except:
                res = 500, {"error":500}
        request.send_response(res[0])
        if type(res[1]) is str:
            request.send_header('Content-type', 'text/html')
            request.end_headers()
            request.wfile.write(res[1].encode())
        elif type(res[1]) is dict:
            request.send_header('Content-type', 'application/json')
            request.end_headers()
            request.wfile.write(json.dumps(res[1]).encode())
        else:
            request.wfile.write(str(res[1]).encode())
        return

    def __init__(self, address = "localhost", port = 8000, sync = True):
        self.bindes = {}
        self.server_address = (address, port)
        self.sync = sync

    def start(self):
        global main_server
        main_server = self
        if self.sync:
            httpd = HTTPServer(self.server_address, CustomHandler)
        else:
            httpd = ThreadedHTTPServer(self.server_address, CustomHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
