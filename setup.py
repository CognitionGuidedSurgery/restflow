#!/usr/bin/python

import codecs
import os
import sys

from distutils.util import convert_path
from fnmatch import fnmatchcase
from setuptools import setup, find_packages

import restflow

def read(fname):
        return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="restflow",
    version=restflow.__version__,
    description="Interactive Hiflow3 Simulation an HTTP Request far away",
    long_description=read("README.md"),
    author=["Alexander Weigl", "Nicolai Schoch"],
    author_email="uiduw@student.kit.edu",
    license="gpl3",
    url="http://github.com/CognitionGuidedSurgery/restflow",
    packages=["restflow"],
    scripts=["run_restflow.py"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GPL 3",
        "Operating System :: Linux",
        "Programming Language :: Python",
        "Framework :: Flask",
    ],

    provides = ['restflow'],
    #requires = ['Flask', 'flask-restful', 'path.py', 'requests'],
    zip_safe=False,
)
