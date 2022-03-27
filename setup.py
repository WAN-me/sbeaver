from setuptools import setup
setup(name='sbeaver',
      version='0.5',
      license='GNU',
      url="https://github.com/wex335/sbeaver",
      platforms='ALL',
      long_description="""# Sbeaver
This is sbeaver - a lightweight and extremely simple http server for creating APIs.

To install sbeaver on your system, you can use the `pip install sbeaver` command, or you can download this repository and run `python setup.py install`

# Usage
```python
import sbeaver

server = sbeaver.Server(address="localhost", port=8000, sync=True)
```
this code will import and make the basic configuration of the sbeaver server in your project
To start, you need to call `server.start()`

Decorators are used to bind paths on the server to internal methods.

sbind is used to bind static paths (e.g. home page)

```python
@server.sbind('/')
def index(request):
    return 200, {'status':'ok'}
```
![image](https://user-images.githubusercontent.com/77948630/159173475-1ef6f935-b6bd-437c-8f6e-e2a789510fb2.png)

You can also bind a regular expression using `bind`

```python
@server.bind(r'/regex/(\w*)(?:\.|/)(\w*)(?:|/)')
def regex(request, param1 = None, param2 = None):
    return 200, {'first':param1, 'second':param2}
```
![image](https://user-images.githubusercontent.com/77948630/159207990-e83826b3-e8d2-47f9-b0c9-1fb6e38a39a7.png)

Or if you can't work with the regex, you can use easy bind(`ebind`)

```python
@server.ebind('/ebind/<submethod>/<method>')
def method(request,  submethod = None, method = None):
    return 200, {'section':submethod, 'method':method}
```

![image](https://user-images.githubusercontent.com/77948630/159208999-4f1dbfe7-83fd-40a5-9ad6-5e8ba6d67962.png)

You can also interact with the user's request. For example, this code will return all known information about a particular request

```python
@server.sbind('/info')
def info(request):
    request.parse_all() # get and save data, url params, ip from request
    return 200, {'info':request.dict}
```
![image](https://user-images.githubusercontent.com/77948630/159173699-b5348ded-99ab-4bf1-ab14-359c728e0b0d.png)

If the function required for the path is not found during request processing, the code404 function is called. It can be assigned by code

```python
@server.code404()
def page_not_found(request):
    return {'error404': f"path {request.path} not found"}
```
![image](https://user-images.githubusercontent.com/77948630/159173717-acbb3011-c612-40c2-8d7e-d2d7ff8be650.png)

Also done with 500 code. When an exception occurs during the processing of a user request, an error will be displayed and the code function will be called

```python
@server.code500()
def internal_server_error(request):
    return {'error500': f"Exception happened"}
```

# Redirecting
You can redirect user to another page using method redirect

Example: 
```python
@server.sbind('/') # static bind
def args(request):
    return sbeaver.redirect(307,'/info') # redirect with data(307 code)
```

# Files
You can return files using method file
```python
@server.sbind('/photo')
def photo(request):
    return sbeaver.file('beaver.png',sbeaver.Types.image.png)
```

""",
      long_description_content_type='text/markdown',
      description='Simple http server for api',
      packages=['sbeaver'],
      author_email='wex335@yandex.ru',
      zip_safe=False)