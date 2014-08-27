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

import functools
import os
import subprocess
from collections import defaultdict

from utils import *
from .hf3configs import *
from config import *


SOLUTION_FILENAME = "_deformedSolution_np{np}_RefLvl{rlvl}_Tstep.{step}.pvtu"
"""Filename of result files written by elasticity.
Filename is parameterized by:

:np: number of parallel threads
:rlvl: refinement level
:step: step
"""


def generate_update(func):
    """

    :param func:
    :return:
    """

    def fn(*args, **kwargs):
        d = dstruct()
        func(d, *args, **kwargs)
        return d

    functools.update_wrapper(fn, func)
    return fn


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
    :param f: str
    :rtype: dict
    """
    return {'Param': {'Mesh': {'Filename': f}}}


def update_output_folder(folder):
    """Returns a fragment for updating the output folder in hf3.

    :param folder: folder path
    :param folder: str
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


class dstruct(defaultdict):
    """A magic class, that creates new config entries on access.
    """
    def __init__(self):
        super(dstruct, self).__init__(lambda: dstruct())

    def __setattr__(self, key, item): self[key] = item

    def __getattr__(self, key): return self[key]


def md(*args):
    """creates an directory silently"""
    try:
        return os.mkdir(*args)
    except OSError as e:
        if e.errno != 17: raise e


class Hiflow3Session(object):
    """This class handles session of the elasticity executable.

    * It holds both configuration files (bcdata and hf3data) in memory.
    * It sets the last mesh as the input of the next run
    * Provides access to results
     """

    def __init__(self, working_dir):
        self._working_dir = path(working_dir)
        self._hf3 = HF3_TEMPLATE_BASIC
        self._bc = BCDATA_TEMPLATE_BASIC

        self._run = 0
        self._step = 0

        # out_path = os.path.join(self.working_dir, RESULTS_DIR)
        md(self.working_dir)
        # md(out_path)
        #self.update_hf3(update_output_folder(out_path))

    @property
    def working_dir(self):
        """the working dir for elasticity (holds all configs and results)"""
        return self._working_dir

    @working_dir.setter
    def working_dir(self, wd):
        self._working_dir = wd

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

    def get_result_files(self):
        """Returns all result files after `SOLUTION_FILENAME`

        :return: a list of path.path
        :rtype: list[path.path]
        """
        wildcard = '*'
        fn = SOLUTION_FILENAME.format(np=wildcard, rlvl=wildcard, step=wildcard)
        resultsd = self.working_dir.listdir(RESULTS_DIR.format(run='*'))
        for rd in resultsd:
            for rf in rd.files(fn):
                yield rf

    def get_result(self, step):
        """Returns the filename for `step`

        This is a pvtu file.

        :rtype: path.path
        """
        import fnmatch

        fn = SOLUTION_FILENAME.format(np="*", rlvl="*", step="%04d" % step)
        for rf in self.get_result_files():
            # print rf.name , fn
            if fnmatch.fnmatch(rf.name, fn):
                return rf


    def _prepare_config(self):
        BC_FILENAME_TEMPATE = "%s/bc_%03d.xml"
        HF3_FILENAME_TEMPATE = "%s/hf3_%03d.xml"
        bcfile = BC_FILENAME_TEMPATE % (self.working_dir, self._run)
        hf3file = HF3_FILENAME_TEMPATE % (self.working_dir, self._run)

        output_dir = self.working_dir / RESULTS_DIR.format(run=self._run)

        output_dir.makedirs_p()

        self.update_hf3(update_bcdata(bcfile))
        self.update_hf3(update_output_folder(output_dir))

        if self._run > 1:
            # set the meshfile from last run
            oldmesh = self.get_result(self._step)
            newmesh = self.working_dir / "input_{step}.vtu".format(step=self._run)
            write_vtu(read_ugrid(oldmesh), newmesh)
            self.update_hf3(update_meshfile(newmesh))

        bcdata = self.bcdataxml()
        hf3xml = self.hf3xml()

        with open(bcfile, 'w') as fh:
            fh.write(bcdata)

        with open(hf3file, 'w') as fh:
            fh.write(hf3xml)

        return hf3file, bcfile


    def run(self):
        """Runs elasticity.

        * First prepares the configuration files for the run (`self._run´).
          * sets the last mesh result as new input mesh
        * Creates output folder

        :raises: BaseException if elasticity returned with errorlevel != 0,
                 checkout `self.workingdir/outptu_{self._run}.txt` for more information.
        :return: something undefined
        """
        self._run += 1

        hf3file, bcfile = self._prepare_config()

        try:
            # proc = subprocess.Popen(
            # [ELASTICITY_PROGRAM, hf3file],
            #stdout=subprocess.PIPE,
            #stderr=subprocess.STDOUT)

            proc = subprocess.Popen(
                ["mpirun", "-np", "8",
                 ELASTICITY_PROGRAM, hf3file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)

            # (stdout, _) = proc.communicate()
            fil = proc.stdout
            proc.wait()

            with open(self.working_dir / "output_%d.txt" % self._run, 'w') as fp:
                fp.write(proc.stdout.read())

            if proc.returncode != 0:
                print proc.returncode
                raise BaseException("Hiflow did terminate with %d" % proc.returncode)
        except OSError as e:
            raise e  # TODO

        steps = int(self.hf3['Param']['Instationary']['MaxTimeStepIts'])
        new_steps = range(1 + self._step, 1 + steps)
        self._step += steps
        return new_steps


    def hf3xml(self):
        """Returns hf3 data structure as xml string
        :rtype: str
        """
        return dict_to_xml(self.hf3)

    def _clean_bcdata(self):
        """Delete empty (None) entries in bc data structure
        """
        param = self.bc['Param']
        new = {}
        for k in param:
            subEmpty = all(map(lambda x: x is None or x == "", param[k].values()))
            if not subEmpty:
                new[k] = param[k]
        self.bc['Param'] = new

    def bcdataxml(self):
        """Returns the bc data as xml string.
        :rtype: str
        """
        self._clean_bcdata()
        return dict_to_xml(self.bc)