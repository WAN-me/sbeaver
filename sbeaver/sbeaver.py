# -*- coding: utf-8 -*-

"""
    Простейший REST API сервер
    Программа была написана: @wex335
    Программа была отрефакторена: @SantaSpeen
"""

# Обратите внимание!!!
# Контент ниже может вас шокировать, или заставить совершить самосуд над разработчиком.
# Не подготовленных людей и детей уберите от экранов.

from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
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
    import zlib
except ImportError:
    print('Failed to import zlib. It will not be possible to decode deflate\n'
          'Run\n\t> pip install zlib \nto install.\n', file=sys.stderr)

try:
    import brotli
except ImportError:
    brotli = None

try:
    import gzip
except ImportError:
    gzip = None


class Types:
    class Application:
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

    class Audio:
        mp3 = 'audio/mpeg'
        wma = 'audio/x-ms-wma'
        realaudio = 'audio/vnd.rn-realaudio'
        wav = 'audio/x-wav'
        ogg = 'audio/ogg'

    class Image:
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

    class Text:
        css = 'text/css'
        csv = 'text/csv'
        html = 'text/html'
        js = 'text/javascript'
        plain = 'text/plain'
        xml = 'text/xml'
        md = 'text/markdown'

    class Video:
        mpeg = 'video/mpeg'
        mp4 = 'video/mp4'
        quicktime = 'video/quicktime'
        wmv = 'video/x-ms-wmv'
        msvideo = 'video/x-msvideo'
        flv = 'video/x-flv'
        webm = 'video/webm'


def open_file(path, file_type, filename=None):
    with open(path, "rb") as f:
        return 200, f.read(-1), file_type, {
            "Content-disposition": f'filename="{filename or path.split(os.sep, 1)[::-1][0]}"'}


def redirect(code, location):
    html = f'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n
    <title>Redirecting...</title>\n
    <h1>Redirecting...</h1>\n
    <p>You should be redirected automatically to target URL: 
    <a href="{location}">{location}</a>. If not click the link.'''
    return code, html, Types.Text.html, {"Location": location}


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Response:

    def __init__(
            self,
            code: int = 200,
            data: str = 'ok',
            mimetype: Types = Types.Text.plain,
            headers: dict = None,
            cookies: dict = None
    ):
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        self.code = code
        self.data = data
        self.mimetype = mimetype
        self.headers = headers
        self.cookies = cookies

    def list(self):
        return self.code, self.data, self.mimetype, self.headers, self.cookies


class Request:

    def parse_all(self):
        self._ip
        self._args
        self.form = {}
        self.data = {}
        self.files = {}
        self._cookies
        encoding = self.headers.get('Content-Encoding')
        if "Content-Length" in self.headers:
            length = int(self.headers.get('Content-Length', '0'))
            self.raw_data = self.req.rfile.read(
                length)  # Получаем сырой контент
            # Если контент сжат gzip ом и модуль импортирован, то декомпрессить
            if encoding in ['gzip', 'x-gzip'] and 'gzip' in sys.modules:
                self.raw_data = gzip.decompress(self.raw_data)
            # Если контент сжат br ом и модуль импортирован, то декомпрессить
            elif encoding in ['br'] and 'brotli' in sys.modules:
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
            self.headers[self.req.headers.keys()[i]] = self.req.headers.values()[
                i]
        return self.headers

    @property
    def _cookies(self):
        self.cookies = {}
        cooks = cookies.SimpleCookie(self.headers.get('Cookie')).items()
        for i in cooks:
            self.cookies[i[0]] = i[1].coded_value
        return self.cookies

    @property
    def _args(self):
        self.args = {}
        if '?' in self.req.path:
            rawargs = urllib.parse.parse_qs(self.splited[1])
            for arg in rawargs:
                self.args[arg] = rawargs[arg][0]
        return self.args

    def __init__(self, req: BaseHTTPRequestHandler, method='GET'):
        self.req = req
        self.splited = req.path.split('?', 1)
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

    def do_HEAD(self):
        main_server.async_worker(self, 'HEAD')

    def do_DELETE(self):
        main_server.async_worker(self, 'DELETE')

    def do_PUT(self):
        main_server.async_worker(self, 'PUT')

    def log_message(self, format, *args):
        if main_server.silence:
            return
        else:
            return BaseHTTPRequestHandler.log_message(self, format, *args)


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
            rr = re.findall(r'(<\w+>)+', path_regex)
            reg = path_regex
            for _ in rr:
                if len(_) > 0:
                    reg = reg.replace(_, r'(\w+)')
            self._bind(reg + '$', func)

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
            self._bind(path + '$', func)

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
        cookies = {}
        content_type = 'text/plain'
        try:
            for bind in self.bindes:  # обработка бинда
                match = re.fullmatch(bind, rr.path)
                if match:
                    res = self.bindes[bind](rr, *match.groups())
                    if type(res) == Response:
                        res = res.list()
                    if type(res) != tuple:
                        res = 200, res
                    break
            else:  # если бинда нету
                if self.__dict__.get('_code404'):  # Попытка получить 404 ошибку
                    res = 404, self._code404(rr)
                else:
                    res = 404, {'error': 404}

            # Content type
            if len(res) >= 3:  # Пользователь знает тип контента
                if len(res) >= 4:  # Есть кастомные заголовки(в виде словаря)
                    if len(res) >= 5:  # Есть куки
                        cookies = res[4]
                    headers = res[3]

                content_type = res[2]  # Отправка типа контента
                result = res[1]
            else:  # Пользователь не знает тип контента
                if type(res[1]) is str:  # Строка, хтмл страница
                    content_type = 'text/html'
                    result = res[1]
                elif type(res[1]) is dict:  # Словарь, жсон обьект
                    content_type = 'application/json'
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
                else:
                    result = str(result).encode()
                res = list(res)
                res[1] = result
            except Exception as e:
                if not main_server.silence:
                    print(
                        f'failed to encode request "{result}" to bytes:\n', file=sys.stderr)
                raise e

        except Exception as e:
            if not main_server.silence:
                print_tb(e.__traceback__)
                print(e, file=sys.stderr)
            try:
                if self.__dict__.get('_code500'):
                    res = 500, json.dumps(self._code500(rr, e)).encode()
                else:
                    res = 500, b'{"error":500}'
                content_type = 'application/json'
            except Exception as t:
                if not main_server.silence:
                    print_tb(t.__traceback__)
                    print(t, file=sys.stderr)
                res = 500, b'{"error":500}'
                content_type = 'application/json'

        request.send_response(res[0])  # Отправляем код. 404, 500 или указанный
        for key in headers.keys():
            request.send_header(key, headers[key])
        for key in cookies.keys():
            request.send_header('Set-Cookie', key + '=' + cookies[key])
        request.send_header('Content-type', content_type)
        request.end_headers()
        try:
            request.wfile.write(res[1])  # отправка ответа
        except BrokenPipeError:
            if not main_server.silence:
                print('The client disconnected ahead of time', file=sys.stderr)
        return

    def __init__(self, address="localhost", port=8000, sync=True, auto_parse=True, silence=False):
        self.bindes = {}
        self.funcs = {}
        self.server_address = (address, port)
        self.port = port
        self.address = address
        self.sync = sync
        self.auto_parse = auto_parse
        self.silence = silence

        if not self.silence:
            if not gzip:
                print('Failed to import gzip. It will not be possible to decode gzip\n'
                      'Run\n\t> pip install gzip \nto install.\n',
                      file=sys.stderr)
            if not brotli:
                print('Failed to import brotli. It will not be possible to decode br\n'
                      'Run\n\t> pip install brotli \nto install.\n',
                      file=sys.stderr)

    def start(self):
        global main_server
        main_server = self
        if self.sync:
            httpd = HTTPServer(self.server_address, CustomHandler)
        else:
            httpd = ThreadedHTTPServer(self.server_address, CustomHandler)
        try:
            if not main_server.silence:
                print(f'sbeaver server started at http://{self.address}:{self.port}')
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
