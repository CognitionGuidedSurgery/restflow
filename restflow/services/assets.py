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
import requests
from flask import request
from flask.ext.restful import Resource


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
        chunk_size = 1024 * 8
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
