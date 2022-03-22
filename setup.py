from setuptools import setup
with open('readme.md','r') as rm:
    setup(name='sbeaver',
        version='0.4',
        license='GNU',
        url="https://github.com/wex335/sbeaver",
        platforms='ALL',
        long_description=rm.read(-1),
        long_description_content_type='text/markdown',
        description='Simple http server for api',
        packages=['sbeaver'],
        author_email='wex335@yandex.ru',
        zip_safe=False)