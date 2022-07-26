# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
packages = ['sbeaver']
requires = []

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python3 -m build')
    os.system('python3 -m twine upload --repository testpypi dist/*')
    os.system('python3 -m twine upload --repository pypi dist/*')
    sys.exit()

about = {}
with open(os.path.join(here, packages[0], '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    package_data={'': ['LICENSE']},
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=packages,
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://github.com/WAN-me/sbeaver/blob/master/README.md',
        'Source': about['__url__'],
    },
    python_requires=">=3.6",
    zip_safe=False
)
