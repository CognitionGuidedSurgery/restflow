#!/usr/bin/python

"""
restflow
========

Interactive Hiflow3 Simulation an HTTP Request far away::

    Author: Alexander Weigl <Alexander.Weigl@student.kit.edu>
            Nicolai Schoch <Nicolai.Schoch@iwr.uni-heidelberg.de>

    License: GPL v3
    Date: 2014-08-30

restflow allows you to run `Hiflow3 <http://hiflow3.org>`_ as a webservice with a rest interface.
The used Hiflow-Binding allowes an interaction with the simulation. You can change the environment or constraints in between all runs.

Please note that HiFlow3 was released under the Academic License Agreement of KIT until version 1.3.
All releases after and including version 1.3 are released under LGPLv3 to support a better community and open source development.

The application ("Interactive HiFlow3 Soft Tissue Simulation"), which is accessed and used for simulation here,
was developed at the Engineering Mathematics and Computing Lab (EMCL) at Heidelberg University as part of
ongoing research within the SFB/TRR 125 (Cognition-Guided Surgery).

"""


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
    long_description=__doc__,
    author=["Alexander Weigl", "Nicolai Schoch"],
    author_email="uiduw@student.kit.edu",
    license="gpl3",
    url="http://github.com/CognitionGuidedSurgery/restflow",
    packages=["restflow"],
    scripts=["share/run_restflow.py"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Framework :: Flask",
    ],

    provides = ['restflow'],
    #requires = ['Flask', 'flask-restful', 'path.py', 'requests'],
    zip_safe=False,
)
