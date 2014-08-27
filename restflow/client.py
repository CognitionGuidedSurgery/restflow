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

"""Client for restflow


"""

__author__ = "Alexander Weigl <uiduw@student.kit.edu>"
__date__ = "2014-07-11"

#!/usr/bin/python

import json

import requests


class HTTPResponseError(BaseException):
    def __init__(self, message, **kwargs):
        super(HTTPResponseError, self).__init__(message)
        self.__dict__.update(kwargs)


class _LowLevel(object):
    """Low level operation on the rest api.
    This class does not hold any, just a configured ..py:class:`requests.Session`

    """

    def __init__(self, url="http://localhost:5000"):
        self._base_url = url
        self.session = requests.Session()

    def url(self, path, *args, **kwargs):
        return self._base_url % (path.format(**kwargs))


    def _handle_json(self, resp):
        print resp.url
        if resp.status_code == 200:
            return resp.json()

        raise HTTPResponseError("HTTPRequest answered with %d. Content: %s" % (resp.status_code, resp.text),
                                response=resp)

    def oneshot(self, *args, **kwargs):
        """Simple HTTP GET request with json response data"""
        resp = self.session.get(self.url(*args, **kwargs))
        return self._handle_json(resp)


    def open_session(self):
        return self.oneshot("/session")

    def close_session(self, token):
        self.session.delete(self.url("/session/{token}", token=token))

    def list_templates(self):
        return self.oneshot("/template")

    def get_template(self, name):
        return self.oneshot("/template/{name}", name=name)

    def get_config(self, token):
        return self.oneshot("/session/{token}", token=token)

    def set_config(self, token, hf3_config, bc_config):
        resp = self.session.put(self.url("/session/{token}", token=token),
                                data={'hf3': hf3_config, 'bc': bc_config})

        return self._handle_json(resp)


    def set_property(self, token, update, config='hf3'):
        resp = self.session.post(self.url("/session/{token}", token=token),
                                 data={"update": json.dumps(update), "config": config})
        return self._handle_json(resp)

    def get_result_list(self, token):
        return self.oneshot("/session/{token}/result")

    def get_result(self, token, step, function, target):
        from contextlib import closing

        with open(target, 'wb') as fp:
            with closing(requests.get(self.url('/session/{token}/result/{step}/{type}',
                                               token=token, step=step, type=function), stream=True)) as r:
                if r.status_code != 200:
                    raise HTTPResponseError("status code is %d" % r.status_code)

                fp.writelines(r.iter_lines())
        return target

    def apply(self, token):
        resp = self.session.get(self.url("/session/{token}/run", token=token))
        return self._handle_json(resp)


class HiFlowRestClient(object):
    """High level api for restflow services

    :param url: the base url for the service, eg. http://localhost:5000
    :type url: str
    """

    def __init__(self, url):
        self._lowlevel = _LowLevel(url)

    def open_simulation(self):
        token = self._lowlevel.open_session()
        return Simulation(self._lowlevel, token)

    def upload_mesh(self, filename=None, url=None):
        """Uploads the given mesh file, or request a download of `url` from the service.


        :param filename: uploads the given the to the server
        :type filename: str
        :param url: server will download the file behind tis URL
        :type url: str

        :return: a identifier of the new created file on the server
        :rtype: str
        """
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
            r = requests.get(self.url("asset"), params={'url': url})

        return r.json()['filename']


class Simulation(object):
    """The simulation is a Hiflow3Session on the server.
    You should not directly create this, ask ..py:meth:`HiFlowRestClient.open_simulation` instead.
    """
    def __init__(self, lowlevel, token):
        self._lowlevel = lowlevel
        self.token = token

        self._local_hf3 = None
        self._local_bc = None

        self._persistent = False

    def __del__(self):
        if not self._persistent:
            try:
                self._lowlevel.close_session(self.token)
                # we should show any exception or else in destructor
            except:
                pass

    @property
    def hf3(self):
        if self._local_hf3 is None:
            self._retrieve_config()
        return self._local_hf3

    @hf3.setter
    def hf3(self, value):
        self._local_hf3 = value

    @property
    def bc(self):
        if self._local_bc is None:
            self._retrieve_config()
        return self._local_bc

    @bc.setter
    def bc(self, value):
        self._local_hf3 = value

    def _retrieve_config(self):
        self._local_hf3, self._local_bc = self._lowlevel.get_config(self.token)

    def _upload_config(self):
        self._lowlevel.set_config(self.token, self._local_hf3, self._local_bc)

    def __call__(self):
        self._upload_config()
        return self._lowlevel.apply(self.token)

    def get_result_files(self):
        return self._lowlevel.get_result_list(self.token)

    def get_result_step(self):
        f = self.get_result_files()
        return range(len(f))

    def get_result(self, step, function='vtu', target=None):
        if not target:
            import tempfile

            target = tempfile.mktemp()
        return self._lowlevel.get_result(self.token, step, function, target)


class RestApiException(BaseException): pass

