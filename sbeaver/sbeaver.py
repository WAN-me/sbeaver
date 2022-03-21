from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from traceback import print_tb
import urllib.parse
import json
import re

def redirect(code,location):
    html = f'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n
    <title>Redirecting...</title>\n
    <h1>Redirecting...</h1>\n
    <p>You should be redirected automatically to target URL: 
    <a href="{location}">{location}</a>. If not click the link.'''
    return code, html

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

class Request():
    def parse_all(self):
        self._ip
        self._headers
        self._args
        self._data
    @property
    def _ip(self):
        self.ip = self.req.client_address[0]
        return self.ip
    @property
    def _headers(self):
        self.headers = {}
        for i in range(len(self.req.headers.values())):
            self.headers[self.req.headers.keys()[i]] = self.req.headers.values()[i]
        return self.headers
    @property
    def _args(self):
        self.args = {}
        if '?' in self.req.path:
            rawargs = urllib.parse.parse_qs(self.splited[1])
            for arg in rawargs:
                self.args[arg] = rawargs[arg][0]
        return self.args
    @property
    def _data(self):
        self.data = {}
        if "Content-Length" in self.req.headers.keys():
            length = int(self.headers.get('Content-Length','0'))
            if length > 0:
                self.rawdata = self.req.rfile.read(length).decode()
                self.data = __parse_data(self.rawdata)
        return self.data
    def __init__(self,req: BaseHTTPRequestHandler):
        self.req = req
        self.splited = req.path.split('?',1)
        self.path = urllib.parse.unquote(self.splited[0])

    def __str__(self) -> str:
        return f'headers: {self.headers}\nargs: {self.args}\ndata: {self.data}' 
    @property
    def dict(self):
        d = self.__dict__
        d.pop('req')
        return d

class CustomHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super(CustomHandler, self).__init__(*args, **kwargs)
    def do_GET(self):
        main_server.async_worker(self)
    def do_POST(self):
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
        rr = Request(request)
        try:
            for bind in self.bindes:
                match = re.fullmatch(bind, rr.path)
                if match:
                    res = self.bindes[bind](rr,*match.groups())
                    break
            else:
                if self.code404:
                    res = 404, self.code404(rr)
                else: res = 404, {'error':404}
                
        except Exception as e:
            print_tb(e.__traceback__)
            print(e)
            try:
                if self.code500:
                    res = 500, self.code500(rr, e)
                else: res = 500, {'error':500}
            except:
                res = 500, {"error":500}
        request.send_response(res[0])
        if res[0] >= 300 and res[0] < 400:
            request.send_header("Location", res[1].split('href="')[1].split('"')[0])

        # Content type
        if len(res) >= 3:
            request.send_header('Content-type', res[3])
            request.end_headers()
            request.wfile.write(res[1].encode())
        else:
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
