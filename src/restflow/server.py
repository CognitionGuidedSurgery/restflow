# -*- encoding: utf-8 -*-
__author__ = 'Alexander Weigl'
__date__ = '2014-07-11'

from .utils import *


from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource
from path import path

app = Flask(__name__)
api = Api(app)

SESSION = {}


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
    """creates a new session/simulation environment"""
    simdata = tempfile.mkdtemp(prefix=name)
    hf3 = merge_dict(HF3_TEMPLATE, HF3_OUTPUTDIR_UPDATE(simdata+"/results"))
    bcdata = BCDATA_TEMPLATE
    SESSION[name] = Session(hf3, bcdata, simdata)

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
        session = get_session()

        steps = request.args['steps']
        deltaT = request.args['deltaT']


        print steps, deltaT

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
api.add_resource(StartSession, '/simulation/new')
api.add_resource(StopSession,  '/simulation/clean')

# Simulation
api.add_resource(BCData,    '/simulation/bc')
api.add_resource(Hf3Data,   '/simulation/hf3')
api.add_resource(RunHiFlow, '/simulation/run')
api.add_resource(Result, '/simulation/result/<string:type>')

