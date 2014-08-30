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
from .. import hf3configs



TEMPLATES = {
    'hf3': hf3configs.HF3_TEMPLATE_BASIC,
    'bc': hf3configs.BCDATA_TEMPLATE_BASIC,
}
"""Configuration templates"""




class TemplateList(Resource):
    def get(self):
        """Returns a list of registered templates
        :return:
        """
        return TEMPLATES.keys()


class Template(Resource):
    def get(self, type):
        try:
            return TEMPLATES[type]
        except:
            return abort(501, "Type %s not valid")

