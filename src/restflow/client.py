#
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

"""
Client for restflow


"""

__author__ = "Alexander Weigl <uiduw@student.kit.edu>"
__date__   = "2014-07-11"


import json

import requests


class HiFlowRestClient(object):
    def __init__(self, url):
        if not url.endswith('/'):
            raise BaseException("url need trailing slash")

        self.base_url = url


    def open_simulation(self):
        r = requests.get(self.url("simulation/new"))
        if r.status_code != 200:
            raise BaseException("status_code != 200")
        token = r.json()['token']
        return Simulation(self, token)

    def upload_mesh(self, filename=None, url = None):
        if filename:
            import os.path
            from requests_toolbelt import MultipartEncoder

            m = MultipartEncoder(
                fields={'file':
                            (os.path.basename(filename),
                             open(filename, 'rb'),
                             'text/plain')})

            r = requests.post(self.url("asset"),
                              data=m, headers={'Content-Type': m.content_type})

        elif url:
            r = requests.get(self.url("asset"), params={'url':url})

        return r.json()['filename']



    def url(self, endpoint):
        return self.base_url + endpoint


class Simulation(object):
    def __init__(self, client, token):
        self.client = client
        self.token = token

    def _get(self, endpoint):
        r = requests.get(self.client.url(endpoint), params={"token": self.token})
        if r.status_code != 200:
            raise RestApiException("result is %d != 200, content=%s" % (
                r.status_code, r.content))
        return r
    def __del__(self):
        try:
            self._get("simulation/clean")
            # we should show any exception or else in destructor
        except:
            pass

    @property
    def hf3(self):
        r = self._get("simulation/hf3")
        return r.json()

    @hf3.setter
    def hf3(self, value):
        r = requests.put(self.client.url("simulation/hf3"),
                          data={
                              "token": self.token,
                              "update": json.dumps(value)
                          })
        return r.json()


    @property
    def bc(self):
        r = self._get("simulation/bc")
        return r.json()

    @bc.setter
    def bc(self, value):
        r = requests.put(self.client.url("simulation/bc"),
                          data={
                              "token": self.token,
                              "update": json.dumps(value)
                          })
        return r.json()


    def __call__(self, steps, deltaT):
        r = requests.get(self.client.url('simulation/run'),
                         params={'token': self.token, 'steps': steps, 'deltaT': deltaT})
        if r.status_code != 200:
            print r.content
            raise RestApiException()

        return


class RestApiException(BaseException): pass

