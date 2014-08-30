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

"""Flask Restful Server for Hiflow3Session.




"""

__author__ = 'Alexander Weigl'
__date__ = '2014-07-11'

from flask import Flask
from flask.ext.restful import Api
from flask_restful_swagger import swagger
from . import config
from .services import *

app = Flask(__name__)
api = Api(app)
api = swagger.docs(api,
                   apiVersion='1.0', api_spec_url='/api/spec',
                   basePath=config.BASE_PATH)


api.add_resource(TemplateList, '/template')
api.add_resource(Template, '/template/<string:type>')
api.add_resource(Assets, '/assets')
api.add_resource(Assets2, '/assets/<string:aid>')
api.add_resource(ResultFunctionsList, '/results')


# Session Management
api.add_resource(SimulationOpen, '/session')
api.add_resource(Simulation, '/session/<string:token>')
api.add_resource(RunSimulation, '/session/<string:token>/run')

# Simulation
api.add_resource(Result, '/session/<string:token>/result/<int:step>/<string:func>')
api.add_resource(ResultList, '/session/<string:token>/result/')
