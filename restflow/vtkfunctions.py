#
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

"""This modules provides functions from the VTK world.

"""

__author__ = "Alexander Weigl <uiduw@student.kit.edu>"
__date__ = "2014-07-10"

try:
    import vtk
    from vtk import *
except ImportError as e:
    print "No VTK Module"

def read_ugrid(filename):
    if filename.endswith(".pvtu"):
        reader = vtk.vtkXMLPUnstructuredGridReader()
    elif filename.endswith(".vtk"):
        reader = vtk.vtkUnstructuredGridReader()
    elif filename.endswith(".vtu"):
        reader = vtk.vtkUnstructuredGridReader()
    else:
        raise BaseException("Illegal filename suffix %s" % filename)

    reader.SetFileName(filename)
    reader.Update()

    return reader.GetOutput()

def write_surface(ugrid, filename):
    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(ugrid)

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputConnection(triangle_filter.GetOutputPort())
    writer.Write()

def write_stl(ugrid, filename):
    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(ugrid)

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

    writer = vtk.vtkSTLWriter()
    writer.SetFileName(filename)
    writer.SetInputConnection(triangle_filter.GetOutputPort())
    writer.Write()

def write_vtu(ugrid, filename, mode = 'ascii'):
    writer = vtk.vtkXMLUnstructuredGridWriter()
    if mode == 'ascii':
        writer.SetDataModeToAscii()
    elif mode == 'binary':
        writer.SetDataModeToBinary()
    elif mode == 'append':
        writer.SetDataModetoAppend()

    writer.SetFileName(filename)
    writer.SetInputData(ugrid)
    writer.Write()

def write_vtk(ugrid, filename):
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(ugrid)
    writer.Write()
