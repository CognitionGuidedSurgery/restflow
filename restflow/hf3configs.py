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

RESULTS_DIR = "results_{run}"

HF3_TEMPLATE_BASIC = {
    'Param': {
        'OutputPathAndPrefix': RESULTS_DIR,
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

BCDATA_TEMPLATE_BASIC = {
    'Param': {

        'BCData': {
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
                'ForcesOrPressures': None,
            }
        }
    }
}