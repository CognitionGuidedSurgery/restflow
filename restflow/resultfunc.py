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


__author__ = 'Alexander Weigl'
from path import path

__all__ = [
    "make_result", "register_result", "get_result",
    "get_stl", "get_vtk", "get_vtp", "vtu"
]

_REGISTER = {}

def make_result(name, filename):
    return get_result(name)(filename)

def get_result(name):
    return _REGISTER[name]


def register_result(name=None, function=None):
    def fn(func):
        n = name or function.__name__
        _REGISTER[n] = func

    if function:
        fn(function)
    else:
        return fn


import tempfile

from .vtkfunctions import *


@register_result("vtu")
def get_vtu(pvtu):
    fn = path(tempfile.mktemp(".vtu", "elasticity_result_request_"))
    write_vtu(read_ugrid(pvtu), fn)
    return fn

@register_result("vtu_a")
def get_vtu(pvtu):
    fn = path(tempfile.mktemp(".vtu", "elasticity_result_request_"))
    write_vtu(read_ugrid(pvtu), fn, mode="append")
    return fn


@register_result("vtu_b")
def get_vtu(pvtu):
    fn = path(tempfile.mktemp(".vtu", "elasticity_result_request_"))
    write_vtu(read_ugrid(pvtu), fn, mode="binary")
    return fn


@register_result("vtk")
def get_vtk(pvtu):
    fn = path(tempfile.mktemp(".vtk", "elasticity_result_request_"))
    write_vtk(read_ugrid(pvtu), fn)
    return fn

@register_result("stl")
def get_stl(pvtu):
    fn = path(tempfile.mktemp(".stl", "elasticity_result_request_"))
    write_stl(read_ugrid(pvtu), fn)
    return fn


@register_result("vtp")
def get_vtp(pvtu):
    fn = path(tempfile.mktemp(".vtp", "elasticity_result_request_"))
    write_surface(read_ugrid(pvtu), fn)
    return fn