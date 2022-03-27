from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from traceback import print_tb
import urllib.parse
import json
import cgi
import sys
import re
import io
import os
try:
    import brotli
except:
    print('Failed to import brotli. It will not be possible to decode br \nPossible not installed; run pip install brotli to fix')
try:
    import gzip
except:
    print('Failed to import gzip. It will not be possible to decode gzip \nPossible not installed; run pip install gzip to fix')
#try:
#    import zlib
#except:
#    print('Failed to import zlib. It will not be possible to decode deflate \nPossible not installed; run pip install zlib to fix')

class Types():
    class aplication():
        jar = 'application/java-archive'
        js = 'application/javascript'   
        ogg = 'application/ogg'   
        pdf = 'application/pdf'
        xhtml = 'application/xhtml+xml'   
        shockwave = 'application/x-shockwave-flash'    
        json = 'application/json'  
        ld_json = 'application/ld+json'  
        xml = 'application/xml'   
        zip = 'application/zip'  
        x_www_form_urlencoded = 'application/x-www-form-urlencoded'  
        other = 'application/octet-stream'   
    class audio():
        mp3 = 'audio/mpeg'
        wma ='audio/x-ms-wma'   
        realaudio = 'audio/vnd.rn-realaudio'   
        wav ='audio/x-wav'   
        ogg = 'audio/ogg'
    class image():
        gif = 'image/gif'
        jpeg = 'image/jpeg'
        pjpeg = 'image/pjpeg'
        png = 'image/png'
        tiff = 'image/tiff'
        micon = 'image/vnd.microsoft.icon'
        icon = 'image/x-icon'
        djvu = 'image/vnd.djvu'
        svg = 'image/svg+xml'
        wap_webp = 'image/vnd.wap.wbmp'
        webp = 'image/webp'
    class text():
        css = 'text/css'    
        csv = 'text/csv'    
        html = 'text/html'    
        js = 'text/javascript'    
        plain = 'text/plain'    
        xml = 'text/xml'    
        md = 'text/markdown'
    class video():
        mpeg = 'video/mpeg'
        mp4 = 'video/mp4'
        quicktime = 'video/quicktime'    
        wmv = 'video/x-ms-wmv'    
        msvideo = 'video/x-msvideo'    
        flv = 'video/x-flv'   
        webm = 'video/webm' 
def file(path, type, filename=None):
    with open(path, "rb") as file:
        return 200, file.read(-1), type, {"Content-disposition": f'attachment; filename="{filename or path.split(os.sep,1)[::-1][0]}"'}

def redirect(code,location):
    html = f'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n
    <title>Redirecting...</title>\n
    <h1>Redirecting...</h1>\n
    <p>You should be redirected automatically to target URL: 
    <a href="{location}">{location}</a>. If not click the link.'''
    return code, html, Types.text.html, {"Location": location}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Request():
    def parse_all(self):
        self._ip
        self._args
        self.form =  {}
        self.data = {}
        self.files = {}
        encoding = self.headers.get('Content-Encoding')
        if "Content-Length" in self.headers:
            length = int(self.headers.get('Content-Length','0'))
            self.raw_data = self.req.rfile.read(length) # Получаем сырой контент
            if encoding in ['gzip','x-gzip'] and 'gzip' in sys.modules: # Если контент сжат gzip ом и модуль импортирован то декомпрессить
                self.raw_data = gzip.decompress(self.raw_data)
            elif encoding in ['br'] and 'brotli' in sys.modules: # Если контент сжат br ом и модуль импортирован то декомпрессить
                self.raw_data = brotli.decompress(self.raw_data)

            try:
                self.data = json.loads(self.raw_data)
            except:
                read_buffer = io.BytesIO(self.raw_data)
                self.headers['Content-Length'] = len(self.raw_data)
                if length > 0:
                    self.form = cgi.FieldStorage(
                        fp=read_buffer,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST'},
                    )
        for key in self.form.keys(): 
            value = self.form.getvalue(key)
            if type(value) is bytes:
                self.files[key] = value
            else:
                self.data[key] = value
        
    @property
    def _ip(self):
        self.ip = self.req.client_address[0]
        if self.ip == '127.0.0.1':
            self.ip = self.headers.get('X-Forwarded-For', '127.0.0.1')
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
    def __init__(self,req: BaseHTTPRequestHandler, method = 'GET'):
        self.req = req
        self.splited = req.path.split('?',1)
        self.path = urllib.parse.unquote(self.splited[0])
        self._headers
        self.method = method
        if main_server.auto_parse:
            self.parse_all()

    def __str__(self) -> str:
        return f'headers: {self.headers}\nargs: {self.args}\ndata: {self.data}' 
    @property
    def dict(self):
        d = self.__dict__
        dell = ['req', 'form', 'files', 'raw_data']
        result = {}
        for key in d:
            if not key in dell:
                result[key] = d[key]
        return result

class CustomHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super(CustomHandler, self).__init__(*args, **kwargs)
    def do_GET(self):
        main_server.async_worker(self, 'GET')
    def do_POST(self):
        main_server.async_worker(self, 'POST')

class AlreadyUsedException(Exception):
    def __init__(self, func):
        self.message = f'Function {func.__name__} already bind on other path'
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message) 

class InvalidParametersCount(Exception):
    def __init__(self, func, need, there_are):
        self.message = f'Function {func.__name__} take {there_are} parameters, but need {need}'
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message) 

class Server():
    def bind(self, path_regex=''):
        def my_decorator(func):
            self._bind(path_regex, func)
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
        
    def _bind(self, regex, func):
        regex = re.compile(regex)
        if func.__qualname__ in self.funcs.keys():
            raise AlreadyUsedException(func)
        need = regex.groups + 1
        if need != func.__code__.co_argcount:
            raise InvalidParametersCount(func, need, func.__code__.co_argcount)
        self.bindes[regex] = func
        self.funcs[func.__qualname__] = func

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
            self._bind(reg+'$', func)
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
            self._bind(path+'$', func)
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator

    def code404(self):
        def my_decorator(func):
            self._code404 = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
    
    def code500(self):
        def my_decorator(func):
            self._code500 = func
            def wrapper(pat):
                return func(pat)
            return wrapper
        return my_decorator
            
    def async_worker(self, request, method):
        rr = Request(request, method) 
        res = []
        headers = {}
        Content_type='text/plain'
        try:
            for bind in self.bindes: # обработка бинда
                match = re.fullmatch(bind, rr.path)
                if match:
                    res = self.bindes[bind](rr,*match.groups())
                    break
            else: # если бинда нету
                if self.__dict__.get('_code404'): # Попытка получить 404 ошибку
                    res = 404, self._code404(rr)
                else: res = 404, {'error':404}

            # Content type
            if len(res) >= 3: # Пользователь знает тип контента
                if len(res) >= 4: # Есть кастомные заголовки(в виде словаря)
                    headers = res[3]

                Content_type = res[2] # Отправка типа контента
                result = res[1]
            else: # Пользователь не знает тип контента
                if type(res[1]) is str: # Строка, хтмл страница
                    Content_type = 'text/html'
                    result = res[1]
                elif type(res[1]) is dict: # Словарь, жсон обьект
                    Content_type = 'application/json'
                    result = res[1]
                else:
                    result = str(res[1])
            data_type = type(result)
            try:
                if data_type is dict:
                    result = json.dumps(result)
                if data_type is bytes:
                    pass
                elif data_type is str:
                    result = result.encode()
                else: result = str(result).encode()
                res = list(res)
                res[1] = result
            except Exception as E:
                print(f'failed to encode request "{result}" to bytes:\n')
                raise E

        except Exception as e:
            print_tb(e.__traceback__)
            print(e)
            try:
                if self.__dict__.get('_code500'):
                    res = 500, json.dumps(self._code500(rr, e)).encode()
                else:
                    res = 500, b'{"error":500}'
                Content_type = 'application/json'
            except Exception as t:
                print_tb(t.__traceback__)
                print(t)
                res = 500, b'{"error":500}'
                Content_type = 'application/json'


        request.send_response(res[0]) # Отправляем код. 404, 500 или указанный
        for key in headers.keys():
            request.send_header(key, headers[key])
        request.send_header('Content-type', Content_type)
        request.end_headers()
        try:
            request.wfile.write(res[1]) # отправка ответа
        except BrokenPipeError:
            print('The client disconnected ahead of time')
        return
        
    def __init__(self, address = "localhost", port = 8000, sync = True, auto_parse = True):
        self.bindes = {}
        self.funcs = {}
        self.server_address = (address, port)
        self.port = port
        self.address = address
        self.sync = sync
        self.auto_parse = auto_parse

    def start(self):
        global main_server
        main_server = self
        if self.sync:
            httpd = HTTPServer(self.server_address, CustomHandler)
        else:
            httpd = ThreadedHTTPServer(self.server_address, CustomHandler)
        try:
            print(f'sbeaver server started at http://{self.address}:{self.port}')
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
