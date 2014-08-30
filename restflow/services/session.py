# -*- encoding: utf-8 -*-
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

import tempfile
import json

from flask.ext.restful import Resource, abort
from flask import request

from ..base import generate_id
from ..hf3binding import Hiflow3Session

SESSION = {}
"""All Hiflow3 Sessions"""

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


def open_session(token):
    """creates a new session/simulation environment
    :param token: the identifier for the new session
    :type token: unicode | str

    :rtype: restflow.hf3binding.Hiflow3Session
    """
    working_dir = tempfile.mkdtemp(prefix=token)
    session = Hiflow3Session(working_dir)
    SESSION[token] = session
    return session


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
            session._bc = json.loads(bc)

        hf3 = request.form.get('hf3', None)
        if hf3:
            session._hf3 = json.loads(hf3)

    def post(self, token):
        """Update hf3 and bc config.

        :param token:
        :return:
        """
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

