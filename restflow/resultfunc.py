__author__ = 'weigl'

from path import path

_REGISTER = {}

def make_result(name, filename):
    return get_result(name)(filename)

def get_result(name):
    return _REGISTER[name]


def register_result(name=None, function=None):
    def fn(func):
        n = name or function.__name__
        _REGISTER[n] = function

    if function:
        fn(function)
    else:
        return fn


import tempfile

from .utils import *


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