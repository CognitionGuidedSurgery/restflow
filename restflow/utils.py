__author__ = 'weigl'

import vtk
from vtk import *

def vtk2surf(a,b):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(a)

    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputConnection(reader.GetOutputPort())

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(b)
    writer.SetInputConnection(triangle_filter.GetOutputPort())
    writer.Write()

def vtk2stl(a,b):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(a)

    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputConnection(reader.GetOutputPort())

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

    writer = vtk.vtkSTLWriter()
    writer.SetFileName(b)
    writer.SetInputConnection(triangle_filter.GetOutputPort())
    writer.Write()


def vtk2vtu(a,b):
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(a)
    reader.Update()
    writer = vtkXmlUnstructuredGridWriter()
    writer.SetDataModeToAscii()
    writer.SetFileName(b)
    writer.SetInputData(reader.GetOutput())
    writer.Write()


def merge_dict(base, update):
    result = {}
    keys = list(base.keys()) + list(update.keys())
    for key in keys:
        try:
            new = update[key]
            try:
                current = base[key]

                #assert key in (update, base)

                if isinstance(new, dict) and isinstance(current, dict):
                    result[key] = merge_dict(current,new)
                else:
                    result[key] = new
            except:
                result[key] = new

        except KeyError as e: # key not in update
            result[key] = base[key]

    return result


def dict_to_xml(map):
    r = ""
    for key, value in map.items():
        if isinstance(value, dict):
            r += "<{n}>\n{recur}\n</{n}>\n".format(n=key, recur=indent(dict_to_xml(value)))
        elif value is None:
            r += "<{n}></{n}>\n".format(n=key, recur=str(value))
        else:
            r += "<{n}>{recur}</{n}>\n".format(n=key, recur=str(value))
    return r


def generate_id():
    import uuid
    return str(uuid.uuid4())


def indent(string):
    return "    " + string.replace("\n", "\n    ")
