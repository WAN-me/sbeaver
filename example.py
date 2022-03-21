import sbeaver

server = sbeaver.Server(address="localhost", port=8000, sync=True)

@server.sbind('/')
def index(request):
    return 200, {'status':'ok'}

@server.bind(r'/regex/(\w*)(?:\.|/)(\w*)(?:|/)')
def regex(request, group_1 = None, group_2 = None):
    return 200, {'section':group_1, 'method':group_2}

@server.bind(r'(/word/)|(\w+)+')
def words(request, *args):
    return 200, {'words':args, "path": request.path}

@server.ebind('/ebind/<submethod>/<method>')
def method(request,  submethod = None, method = None):
    return 200, {'section':submethod, 'method':method}

@server.sbind('/info')
def info(request):
    return 200, {'info':request.__dict__}

@server.code404()
def page_not_found(request):
    return {'error404': f"path {request.path} not found"}

@server.code500()
def internal_server_error(request):
    return {'error500': f"Exception happened"}

server.start()