import sbeaver

server = sbeaver.Server(address="localhost", port=8000, sync=True)

@server.bind('/')
def index(request, args):
    return 200, {'status':'ok'}

@server.bind(r'/regex/(\w*)(?:\.|/)(\w*)(?:|/)')
def regex(request, args):
    return 200, {'section':args[0], 'method':args[1]}

@server.bind(r'/info')
def info(request, args):
    print(args)
    return 200, {'info':request.__dict__}

@server.code404()
def page_not_found(request):
    return {'error404': f"path {request.path} not found"}

@server.code500()
def internal_server_error(request):
    return {'error500': f"Exception happened"}

server.start()