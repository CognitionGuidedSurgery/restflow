# -*- encoding: utf-8 -*-
__author__ = 'Alexander Weigl'
__date__ = '2014-07-11'

from .utils import *

from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)

HF3_MESH_BCDATA_FILENAME_UPDATE = lambda bcfile: {'Param': {'Mesh': {'BCdataFilename': bcfile}}}
HF3_OUTPUTDIR_UPDATE = lambda bcfile: {'Param': {'OutputPathAndPrefix': bcfile}}

HF3_TEMPLATE = {
    'Param': {
        'OutputPathAndPrefix': 'SimResults/elasticitySimulation_',
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
            'PreconditionerName': 'precond',
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

SESSION = {}

class Session(object):
    def __init__(self, hf3, bcdata, simstate):
        self.hf3, self.bcdata, self.simstate = hf3, bcdata, simstate


    def hf3xml(self):
        return dict_to_xml(self.hf3)

    def _clean_bcdata(self):
        param = self.bcdata['Param']
        new = {}
        for k in param:
            subEmpty = all(map(lambda x: x is None or x == "", param[k].values()))
            if not subEmpty:
                new[k] = param[k]
        self.bcdata['Param'] = new

    def bcdataxml(self):
        self._clean_bcdata()
        return dict_to_xml(self.bcdata)

def get_session(token = None):
    if token is None:
        token = request.form.get('token', request.args.get('token'))

    if token is None:
        abort(502, message="token needed")

    try:
        return SESSION[token]
    except KeyError as e:
        abort(501, message = "Session unknown", code=1)

import tempfile

def open_session(name):
    hf3 = merge_dict(HF3_TEMPLATE, HF3_OUTPUTDIR_UPDATE(tempfile.mkdtemp(prefix=name)))
    bcdata = BCDATA_TEMPLATE
    SESSION[name] = Session(hf3, bcdata, None)

open_session("0") #DEBUG purpose

class StartSession(Resource):
    def get(self):
        i = generate_id()
        open_session(i)
        return {'token': i}

class ShowSession(Resource):
    def get(self):
        token = request.args['token']
        s = SESSION[token]
        return (s.hf3, s.bcdata, s.simstate), 200

class StopSession(Resource):
    def get(self):
        token = request.form['token']
        try:
            del SESSION[token]
            #TODO delete simulation data
            return "ok"
        except KeyError as e:
            abort(501, message = "Session unknown", code=1)

class GetTemplate(Resource):
    def get(self, type):
        if type=='hf3':
            return HF3_TEMPLATE

        if type == 'bc':
            return BCDATA_TEMPLATE

        return "Type %s not valid" % type, 501

import json


class Hf3Data(Resource):
    def get(self):
        return get_session().hf3

    def put(self):
        try:
            session = get_session()
            update = json.loads(request.form['update'])
            session.hf3 = merge_dict(session.hf3, update)
            return session.hf3
        except KeyError as e:
            return abort(502, "update Parameter not given")

class BCData(Resource):
    def get(self):
        return get_session().bcdata

    def put(self):
        try:
            session = get_session()
            update = json.loads(request.form['update'])
            session.bcdata = merge_dict(session.bcdata, update)
            return session.bcdata
        except KeyError as e:
            return abort(502, "update Parameter not given")

class RunHiFlow(Resource):
    def get(self):
        token = request.args['token']
        session = SESSION[token]

        steps = request.args['steps']
        print steps

        print session.hf3xml()
        print session.bcdataxml()

        print "Execute hiflow3 ..."

        return "ok"

class Result(Resource):
    def get(self, type):
        pass

import requests, urllib

class Assets(Resource):
    def get(self):
        url = request.args['url']
        filename = tempfile.mktemp(prefix="asset_")
        chunk_size = 1024*8
        r = requests.get(url, stream=True)

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        return {'filename':filename}

    def post(self):
        return "not implemented"


api.add_resource(GetTemplate, '/template/<string:type>')
api.add_resource(Assets, '/assets')

# Session Management
api.add_resource(StartSession, '/simulation/start')
api.add_resource(StopSession,  '/simulation/clean')

# Simulation
api.add_resource(BCData, '/simulation/bc')
api.add_resource(Hf3Data, '/simulation/hf3')
api.add_resource(RunHiFlow, '/simulation/result/<string:type>')

