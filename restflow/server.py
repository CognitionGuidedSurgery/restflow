# -*- encoding: utf-8 -*-
__author__ = 'Alexander Weigl'
__date__ = '2014-07-11'

import tempfile
import json
import requests

from .utils import *
from .hiflow3 import *

from flask import Flask, request
from flask.ext.restful import  abort, Api, Resource

app = Flask(__name__)
api = Api(app)

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
    :rtype: restflow.hiflow3.Hiflow3Session

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


class Simulation(Resource):

    def put(self):
        """Starts a new session.

        Calling this service allocates a new Hiflow3Session on the
        server side with a fresh working directory.

        :reqheader Authorization:

        :statuscode 200: no error


        """
        i = generate_id()
        open_session(i)
        return {'token': i}

    def get(self):
        """Returns every information about current session state.

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid

        """
        token = request.args['token']
        s = SESSION[token]
        return (s.hf3, s.bcdata, s.simstate), 200

    def delete(self):
        """deallocate the server resources.

        This call deletes the working directory
        and every in memory data.

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid

        """

        token = request.form['token']
        try:
            del SESSION[token]
            # TODO delete simulation data
            return "ok"
        except KeyError as e:
            abort(501, message="Session unknown", code=1)

    def post(self, token):
        """Update the datasructure

        :query token: the authorization token

        :statuscode 200: no error
        :statuscode 405: the token is invalid
        """
        pass


class Template(Resource):
    TEMPLATES = {
        'hf3': {},
        'bc' : {},
        'softtissue_hf3' :{}
    }
    def get(self, type):
        try:
            return TEMPLATES[type]
        except:
            return abort(501, "Type %s not valid")

class RunSimulation(Resource):

    def get(self):
        session = get_session()

        steps = request.args['steps']
        deltaT = request.args['deltaT']

        print steps, deltaT

        return "ok"


class Result(Resource):
    def get(self, token, run_id, apply):
        pass


class Assets(Resource):
    def get(self):
        """Retrieve an asset form the given url.

        :returns: the id for the resource on the server

        :query url: an well-formed url
        :statuscode 200: everything alright
        :statuscode xxx: everything exploded

        """
        url = request.args['url']
        filename = tempfile.mktemp(prefix="asset_")
        chunk_size = 1024*8
        r = requests.get(url, stream=True)

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        return {'filename': filename}

    def post(self):
        """Retrieve an asset, uploaded in the post data.

        :returns: the id for the resource on the server

        :query url: an well-formed url
        :statuscode 200: everything alright
        :statuscode xxx: everything exploded
        """
        pass


api.add_resource(Template, '/template/<string:type>')
api.add_resource(Assets, '/assets')

# Session Management
api.add_resource(Simulation, '/session/<string:token>', '/session')
api.add_resource(RunSimulation, '/session/<string:token>/run')

# Simulation
api.add_resource(Result, '/session/<string:token>/result/<int:type>/<string:apply>')
