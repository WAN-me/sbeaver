from .sbeaver import Server, manage_files 
server = Server(sync=False)
@server.bind('/(.*)')
def all(req, filename='index.html'):
    return manage_files(req)
server.start()