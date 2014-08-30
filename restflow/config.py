#-*- encoding: utf-8 -*-
# Copyright (C) 2013-2014 Alexander Weigl, Nicolai Schoch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Configuration


"""

__author__ = 'Alexander Weigl'

import os

ELASTICITY_PROGRAM = os.environ.get("ELASTICIY",
                                    "/home/weigl/workspace/hiflow_1.4/build/examples/elasticity/elasticity")
"""Path to the elasticity executable. If $ELASTICITY is set in the environment, it will be taken"""


BIND_SOCKET = os.environ.get('RESTFLOW_BIND', "0.0.0.0")
PORT        = os.environ.get('RESTFLOW_PORT', "8002")
BASE_PATH   = os.environ.get("RESTFLOW_BASE_PATH", "http://%s:%s/" %(BIND_SOCKET, PORT))