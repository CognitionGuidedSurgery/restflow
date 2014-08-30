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

from flask.ext.restful import Resource, abort
from flask.helpers import send_file

from ..base import generate_id
from ..hf3binding import Hiflow3Session

from .session import get_session
from .. import resultfunc


class RunSimulation(Resource):
    """Start the simulation

    """
    def get(self, token):
        session = get_session(token)
        return session.run()


class ResultFunctionsList(Resource):
    def get(self):
        return resultfunc._REGISTER.keys()


class ResultList(Resource):
    def get(self, token):
        session = get_session(token)
        return session.get_result_files()


class Result(Resource):
    def get(self, token, step, func):
        session = get_session(token)
        filename = session.get_result(step)
        result_fn = resultfunc.make_result(func, filename)
        return send_file(result_fn, as_attachment=True)
