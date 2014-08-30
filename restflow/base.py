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

""" base functions for the whole package

"""

__author__ = 'Alexander Weigl <uiduw@student.kit.edu>'

import abc

class AbstractHf3Session(object):
    """Abstract base class for the Remote or Local Hiflow3 session.

    """
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._hf3 = {}
        self._bc = {}

    @property
    def hf3(self):
        """hf3 data structure (environment, solver settings)"""
        return self._hf3

    @hf3.setter
    def hf3(self, new_value):
        self._hf3 = new_value

    @property
    def bc(self):
        """bc data structure (constraints"""
        return self._bc

    @bc.setter
    def bc(self, value):
        self._bc = value

    def update_hf3(self, to_merged):
        """update the hf3 data structure with the given fragment

        :param to_merged: fragment for update
        :type to_merged: dict
        :return: None
        """
        self.hf3 = merge_dict(self.hf3, to_merged)

    def update_bc(self, to_merged):
        """update the bc data structure with the given fragment

        :param to_merged: fragment for update
        :type to_merged: dict
        :return: None
        """
        self.bc = merge_dict(self.bc, to_merged)


    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def get_result(self, step):
        pass

def update_bcdata(bcfilename):
    """Returns a dictionary fragment for updating the bcdata field.

    :param bcfilename: filename to the bcdata file
    :type bcfilename: str
    :return: a dictionary
    :rtype: dict
    """
    return {'Param': {'Mesh': {'BCdataFilename': bcfilename}}}


def update_meshfile(f):
    """Returns a dictionary fragment for updating the mesh filename in hf3.

    :param f: filename of mesh file
    :type f: str
    :rtype: dict
    """
    return {'Param': {'Mesh': {'Filename': f}}}


def update_output_folder(folder):
    """Returns a fragment for updating the output folder in hf3.

    :param folder: folder path
    :type folder: str
    :rtype: dict
    """
    if not folder.endswith("/"):
        folder += "/"
    return {'Param': {'OutputPathAndPrefix': folder}}


def update_runtime_informations(steps, duration):
    """Returns a fragment for updating the amount of steps and duration of a step.

    :param steps: amount of steps to take
    :type steps: float
    :param duration: duration (delta time) of a step
    :type duration: float
    :rtype: dict
    """
    return {'Param': {'Instationary': None}}


from collections import defaultdict

class dstruct(defaultdict):
    """A magic class, that creates new config entries on access.
    """
    def __init__(self):
        super(dstruct, self).__init__(lambda: dstruct())

    def __setattr__(self, key, item): self[key] = item

    def __getattr__(self, key): return self[key]



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
    """

    :param map:
    :return:
    """
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
