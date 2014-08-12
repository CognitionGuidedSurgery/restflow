# -*- encoding: utf-8 -*-
from flask.helpers import send_file

__author__ = 'Alexander Weigl'
__date__ = '2014-07-11'

import tempfile
import json
import requests

from .utils import *
from .hf3binding import *

from flask import Flask, request
from flask.ext.restful import  abort, Api, Resource
from flask_restful_swagger import swagger

app = Flask(__name__)
api = Api(app)
api = swagger.docs(api, apiVersion='0.1', api_spec_url='/api/spec', basePath="http://i61p154.itec.uka.de:8002")

SESSION = {}

__all__ = ['get_session', 'open_session',
           'Session', 'Result',
           'GetTemplate', 'Assets']


def get_session(token=None):
    """finds and returns the session for the current request

    :param token:
    :type token: unicode or str

    :returns: the session for the current requests
                or raise an exception
    :rtype: restflow.hf3binding.Hiflow3Session

    """

    if token is None:
        token = request.form.get('token', request.args.get('token'))

    if token is None:
        abort(502, message="token needed")

    try:
        return SESSION[token]
    except KeyError as e:
        abort(501, message="Session unknown", code=1)


def open_session(name):
    """creates a new session/simulation environment"""
    working_dir = tempfile.mkdtemp(prefix=name)
    session = Hiflow3Session(working_dir)
    SESSION[name] = session

open_session("0")  # DEBUG purpose

class SimulationOpen(Resource):
     def get(self):
        """Starts a new session.

        Calling this service allocates a new Hiflow3Session on the
        server side with a fresh working directory.

        :reqheader Authorization:

        :statuscode 200: no error

        """
        i = generate_id()
        open_session(i)
        return {'token': i}

class Simulation(Resource):
    def get(self, token):
        """Returns every information about current session state.

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid

        """
        s = get_session(token)
        return {'hf3': s.hf3, 'bc': s.bc}, 200

    def delete(self, token):
        """deallocate the server resources.

        This call deletes the working directory
        and every in memory data.

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid

        """
        try:
            tok = get_session(token)
            del tok
            del SESSION[token]
            # TODO delete simulation data
            return "ok"
        except KeyError as e:
            abort(501, message="Session unknown", code=1)

    def put(self, token):
        """Update the datasructure

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid
        """
        session = get_session(token)

        bc = request.form.get('bc', None)
        if bc:
            session._bc = bc

        hf3 = request.form.get('hf3', None)
        if hf3:
            session._hf3 = hf3

    def post(self, token):
        session = get_session(token)

        print request.form
        update = json.loads(request.form['update'])
        config = request.form.get('config', 'hf3')

        if config == 'hf3':
            session.update_hf3(update)

        elif config == 'bc':
            session.update_bc(update)

        else:
            abort(501, message="Wrong config value")





def insert_key(d, key, value):
    """

    :param d:
    :param key:
    :param value:
    :return:
    """
    if isinstance(key, str):
        key = key.split("/")

    k = key[0]

    if len(key) == 1:
        d[k] = value
    else:
        if not k in d:
            d[k] = {}

        if isinstance(d[k], dict):
            insert_key(d[k], key[1:], value)





from restflow import hf3configs
TEMPLATES = {
    'hf3': hf3configs.HF3_TEMPLATE_BASIC,
    'bc' : hf3configs.BCDATA_TEMPLATE_BASIC,
    }

class TemplateList(Resource):
    def get(self):
        return TEMPLATES.keys()

class Template(Resource):
    def get(self, type):
        try:
            return TEMPLATES[type]
        except:
            return abort(501, "Type %s not valid")

class RunSimulation(Resource):
    def get(self, token):
        session = get_session(token)
        return session.run()

from restflow import resultfunc

class ResultFunctionsList(Resource):
    def get(self):
        return resultfunc._REGISTER.keys()

def ResultList(Resource):
    def get(self, token):
        session = get_session(token)
        return session.get_result_files()

class Result(Resource):
    def get(self, token, step, func):
        session = get_session(token)
        filename = session.get_result(step)
        result_fn = resultfunc.make_result(func, filename)
        return send_file(result_fn, as_attachment=True)


class Assets(Resource):
    def post(self):
        """Retrieve an asset form the given url.

        :returns: the id for the resource on the server

        :query url: an well-formed url
        :statuscode 200: everything alright
        :statuscode 400: everything exploded

        """
        url = request.args['url']
        filename = tempfile.mktemp(prefix="asset_")
        chunk_size = 1024*8
        r = requests.get(url, stream=True)

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        return {'filename': filename}

    def put(self):
        """Retrieve an asset, uploaded in the post data.

        :returns: the id for the resource on the server

        :query url: an well-formed url
        :statuscode 200: everything alright
        :statuscode 400: everything exploded
        """
        pass

class Assets2(Resource):
    def get(self, aid):
        """
        Download given asset
        :param aid:
        :return:
        """
        pass

    def delete(self, aid):
        pass

api.add_resource(TemplateList, '/template')
api.add_resource(Template, '/template/<string:type>')
api.add_resource(Assets, '/assets')
api.add_resource(Assets2, '/assets/<string:aid>')
api.add_resource(ResultList, '/results')


# Session Management
api.add_resource(SimulationOpen, '/session')
api.add_resource(Simulation, '/session/<string:token>')
api.add_resource(RunSimulation, '/session/<string:token>/run')

# Simulation
api.add_resource(Result, '/session/<string:token>/result/<int:type>/<string:apply>')
api.add_resource(ResultList, '/session/<string:token>/result/')
