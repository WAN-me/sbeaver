import sbeaver
from sbeaver import Response

server = sbeaver.Server(address="localhost", port=8008, sync=True)


@server.sbind('/')  # static bind
def args(request: sbeaver.Request):
    return sbeaver.redirect(307, '/info')  # redirect with data(307 code)


@server.bind(r'/regex/(\w*)(?:\.|/)(\w*)(?:|/)')  # bind by regex
def regex_bind(request: sbeaver.Request, param1=None, param2=None):  # params from regex(capture groups)
    return 200, {'first': param1, 'second': param2}


@server.ebind('/ebind/<submethod>/<method>')  # bind by <some> construction
def method(request: sbeaver.Request, submethod=None, method=None):
    return 200, {'section': submethod, 'method': method}


@server.sbind('/info')
def info(request: sbeaver.Request):
    request.parse_all()  # get and save data, url params, ip from request
    return request.dict  # return all known data about request


@server.sbind('/cookies')
def cookies(request: sbeaver.Request):
    print(request.cookies)
    return Response(200, request.dict, cookies={'ff': '1d'})


@server.sbind('/photo')
def photo(request: sbeaver.Request):
    return sbeaver.open_file('beaver.png', sbeaver.Types.Image.png)


@server.sbind('/docs')
def docs(request: sbeaver.Request):
    return sbeaver.open_file('README.md', sbeaver.Types.Text.md)


@server.code404()  # edit 404 error
def page_not_found(request: sbeaver.Request):
    return {'error404': f"path {request.path} not found"}


@server.code500()  # edit 500 error
def internal_server_error(request: sbeaver.Request, Exception):
    return {'error500': f"{Exception} happened"}


if __name__ == '__main__':

    server.start()
