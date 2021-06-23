#!/usr/bin/env python
import codecs
import re
import os
from setuptools import setup, find_packages

VERSION_RE = re.compile(r""".*__version__ = ["'](.*?)['"]""", re.S)
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


def _load_readme():
    readme_path = os.path.join(PROJECT_DIR, 'README.md')
    with codecs.open(readme_path, 'r', 'utf-8') as f:
        return f.read()


def _load_version():
    init_path = os.path.join(PROJECT_DIR, 'tuyalinksdk', '__init__.py')
    with open(init_path) as fp:
        return VERSION_RE.match(fp.read()).group(1)

setup(
    name='tuyalinksdk',
    version=_load_version(),
    license='License :: OSI Approved :: MIT License',
    description='TuyaOS Link SDK for Python',
    long_description=_load_readme(),
    long_description_content_type='text/markdown',
    author='Tuya SDK Common Runtime Team',
    url='https://github.com/tuya/tuyaos-link-sdk-python.git',
    packages=find_packages(include=['tuyalinksdk*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'paho-mqtt>=1.5.1',
        'pycryptodome>=3.10.1',
        'qrcode[pil]',
        'coloredlogs'
    ],
    python_requires='>=3.6',
)
