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

from utils import merge_dict, dict_to_xml
import functools

def generate_update(func):
    def fn(*args, **kwargs):
        d = dstruct()
        func(d, *args, **kwargs)
        return d
    functools.update_wrapper(fn, func)
    return fn


def update_bcdata(bcfilename):
    return {'Param': {'Mesh': {'BCdataFilename': bcfilename}}}

def update_output_folder(folder):
    return {'Param': {'OutputPathAndPrefix': folder}}

def update_runtime_informations(steps, duration):
    return {'Param' : {'Instationary': None}}

RESULTS_DIR = "results/"

HF3_TEMPLATE = {
    'Param': {
        'OutputPathAndPrefix': RESULTS_DIR ,
        'Mesh': {
            'Filename': None,
            'BCdataFilename': None,
            'InitialRefLevel': 0,
        },
        'LinearAlgebra': {
            'Platform': 'CPU',
            'Implementation': 'Naive',
            'MatrixFormat': 'CSR',
        },
        'ElasticityModel': {
            'density': 1,
            'lambda': 0,
            'mu': 42,
            'gravity': -9.81,
        },
        'QuadratureOrder': 2,
        'FiniteElements': {
            'DisplacementDegree': 1,
        },
        'Instationary': {
            'SolveInstationary': 1,
            'DampingFactor': 1.0,
            'RayleighAlpha': 0.0,
            'RayleighBeta': 0.2,
            'Method': 'Newmark',
            'DeltaT': 0.05,
            'MaxTimeStepIts': 10,
        }
        ,
        'LinearSolver': {
            'SolverName': 'iterativeCG',
            'MaximumIterations': 1000,
            'AbsoluteTolerance': 1.e-8,
            'RelativeTolerance': 1.e-20,
            'DivergenceLimit': 1.e6,
            'BasisSize': 1000,
            'Preconditioning': 1,
            'PreconditionerName': 'GAUSS_SEIDEL',
            'Omega': '2.5',
            'ILU_p': '2.5',
        },
        'ILUPP': {
            'PreprocessingType': 0,
            'PreconditionerNumber': 11,
            'MaxMultilevels': 20,
            'MemFactor': 0.8,
            'PivotThreshold': 2.75,
            'MinPivot': 0.05
        }}
}

BCDATA_TEMPLATE = {
    'Param': {
        'FixedConstraintsBCs': {
            'NumberOfFixedDirichletPoints': None,
            'fDPoints': None,
            'fDisplacements': None,
        },
        'DisplacementConstraintsBCs': {
            'NumberOfDisplacedDirichletPoints': None,
            'dDPoints': None,
            'dDisplacements': None,
        },
        'ForceOrPressureBCs': {
            'NumberOfForceOrPressureBCPoints': None,
            'ForceOrPressureBCPoints': None,
            'ForcesOrPressures':None,
        }
    }
}

import os.path, os, subprocess
from collections import defaultdict

class dstruct(defaultdict):
    def __init__(self):
        super(dstruct, self).__init__(lambda: dstruct())

    def __setattr__(self, key, item): self[key] = item
    def __getattr__(self, key): return self[key]

def md(*args):
    try:
        return os.mkdir(*args)
    except OSError as e:
        if e.errno != 17: raise e

class Hiflow3Session(object):
    """This class handles session of the elasticity executable.
    It holds both configuration files (bcdata and hf3data) in memory.


     """

    def __init__(self, working_dir):
        self._working_dir = working_dir
        self._hf3 = HF3_TEMPLATE
        self._bc = BCDATA_TEMPLATE
        self._run = 0
        out_path = os.path.join(self.working_dir, RESULTS_DIR)
        md(self.working_dir)
        md(out_path)
        self.update_hf3(update_output_folder(out_path))

    @property
    def working_dir(self):
        return self._working_dir

    @working_dir.setter
    def working_dir(self, wd): self._working_dir = wd


    @property
    def hf3(self):
        return self._hf3

    @hf3.setter
    def hf3(self, new_value): self._hf3 = new_value

    @property
    def bc(self):
        return self._bc

    @bc.setter
    def bc(self, value):
        self._bc = value

    def update_hf3(self, to_merged):
        self.hf3 = merge_dict(self.hf3, to_merged)

    def update_bc(self, to_merged):
        self.bc = merge_dict(self.bc, to_merged)

    def run(self):

        BC_FILENAME_TEMPATE = "%s/bc_%03d.xml"
        HF3_FILENAME_TEMPATE = "%s/hf3_%03d.xml"
        bcfile =  BC_FILENAME_TEMPATE % (self.working_dir, self._run)
        hf3file = HF3_FILENAME_TEMPATE % (self.working_dir, self._run)

        self.update_hf3(update_bcdata(bcfile))

        bcdata =  self.bcdataxml()
        hf3xml =  self.hf3xml()

        with open(bcfile, 'w') as fh:
            fh.write(bcdata)

        with open(hf3file, 'w') as fh:
            fh.write(hf3xml)


        ELASTICITY_PROGRAM = "/home/weigl/workspace/hiflow_1.4/build/examples/elasticity/elasticity"

        import StringIO


        proc = subprocess.Popen(
            [ELASTICITY_PROGRAM, hf3file],
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)

        #(stdout, _) = proc.communicate()
        fil = proc.stdout
        while True:
            print fil.readline(),

#        print stdout
        proc.wait()
        if proc.returncode != 0:
            print proc.returncode
            #TODO error message, handling

        return True


    def hf3xml(self):
        return dict_to_xml(self.hf3)

    def _clean_bcdata(self):
        param = self.bc['Param']
        new = {}
        for k in param:
            subEmpty = all(map(lambda x: x is None or x == "", param[k].values()))
            if not subEmpty:
                new[k] = param[k]
        self.bc['Param'] = new

    def bcdataxml(self):
        self._clean_bcdata()
        return dict_to_xml(self.bc)