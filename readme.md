# Sbeaver
This is sbeaver - a lightweight and extremely simple http server for creating APIs.

To install sbeaver on your system, you can use the `pip install sbeaver` command, or you can download this repository and run `python setup.py install`

# Usage
```
import sbeaver

server = sbeaver.Server(address="localhost", port=8000, sync=True)
```
this code will import and make the basic configuration of the sbeaver server in your project
To start, you need to call `server.start()`

Decorators are used to bind paths on the server to internal methods.

```
@server.bind('/')
def index(request):
    return 200, {'status':'ok'}
```
![image](https://user-images.githubusercontent.com/77948630/159173475-1ef6f935-b6bd-437c-8f6e-e2a789510fb2.png)

you can also interact with the user's request. For example, this code will return all known information about a particular request
```
@server.bind('/info')
def info(request):
    return 200, {'info':request.__dict__}
```
![image](https://user-images.githubusercontent.com/77948630/159173699-b5348ded-99ab-4bf1-ab14-359c728e0b0d.png)

If the function required for the path is not found during request processing, the code404 function is called. It can be assigned by code
```
@server.code404()
def page_not_found(request):
    return {'error404': f"path {request.path} not found"}
```
![image](https://user-images.githubusercontent.com/77948630/159173717-acbb3011-c612-40c2-8d7e-d2d7ff8be650.png)

Also done with 500 code. When an exception occurs during the processing of a user request, an error will be displayed and the code function will be called

```
@server.code500()
def internal_server_error(request):
    return {'error500': f"Exception happened"}
```
