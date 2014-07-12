__author__ = 'Alexander Weigl'

import json

import requests


class HiFlowRestClient(object):
    def __init__(self, url):
        if not url.endswith('/'):
            raise BaseException("url need trailing slash")

        self.base_url = url


    def open_simulation(self):
        r = requests.get(self.url("simulation/start"))
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
            raise RestApiException()

        return


class RestApiException(BaseException): pass

