__author__ = 'weigl'

try:
    import vtk
    from vtk import *

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
        surface_filter.SetInputConnection(ugrid)

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

except ImportError as e:
    print "No VTK Module"


def merge_dict(base, update):
    """merges to dictionaries

    >>> merge_dict({}, {})
    {}
    >>> merge_dict({}, {'a':1})
    {'a':1}
    >>> merge_dict({'a':1},{'a':2, 'b':1})
    {'a':2,'b':1}
    """
    result = {}
    keys = list(base.keys()) + list(update.keys())
    for key in keys:
        try:
            new = update[key]
            try:
                current = base[key]

                # assert key in (update, base)

                if isinstance(new, dict) and isinstance(current, dict):
                    result[key] = merge_dict(current, new)
                else:
                    result[key] = new
            except:
                result[key] = new

        except KeyError as e:  # key not in update
            result[key] = base[key]

    return result


def dict_to_xml(map):
    r = ""
    for key, value in map.items():
        if isinstance(value, dict):
            r += "<{n}>\n{recur}\n</{n}>\n".format(n=key,
                                                   recur=indent(dict_to_xml(value)))
        elif value is None:
            r += "<{n}></{n}>\n".format(n=key, recur=str(value))
        else:
            r += "<{n}>{recur}</{n}>\n".format(n=key, recur=str(value))
    return r


def generate_id():
    import uuid
    return str(uuid.uuid4())


def indent(string, prefix="   "):
    """indent the given string by `prefix`

        :param str string: the string to indent
        :param str prefix: the indent characters


        >>> indent("a\nb\nc")
        "    a\n    b\n    c\n"
    """
    return prefix + string.replace("\n", "\n"+prefix)
