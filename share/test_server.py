#!/usr/bin/python

import json , requests, see, pprint

class HTTPResponseError(BaseException):
    def __init__(self, message, **kwargs):
        super(HTTPResponseError, self).__init__(message)
        self.__dict__.update(kwargs)


def url(s, **kwargs):
    return "http://localhost:5000%s" % (s.format(**kwargs))


def _handle_json(resp):
    if resp.status_code == 200:
        return resp.json()

    raise HTTPResponseError("HTTPRequest answered with %d. Content: %s" % (resp.status_code, resp.text),
                            response=resp)


def open_session():
    resp = requests.get(url("/session"))
    if resp.status_code == 200:
        return resp.json()['token']
    raise BaseException()


def list_templates():
    resp = requests.get(url("/template"))
    if resp.status_code == 200:
        return resp.json()


def get_template(name):
    resp = requests.get(url("/template/{name}", name=name))
    return _handle_json(resp)


def get_config(token):
    resp = requests.get(url("/session/{token}", token=token))
    return _handle_json(resp)


def set_config(token, hf3_config, bc_config):
    resp = requests.put(url("/session/{token}", token=token),
                        data={'hf3': hf3_config, 'bc': bc_config})

    return _handle_json(resp)


def set_property(token, update, config='hf3'):
    resp = requests.post(url("/session/{token}", token=token),
                         data={"update": json.dumps(update), "config": config})
    return _handle_json(resp)


def apply(token):
    resp = requests.get(url("/session/{token}/run", token=token))
    return _handle_json(resp)


print "Templates:"
print list_templates()

token = open_session()
print token

set_property(token, {"Param": {
    "ElasticityModel": {
        "density": 2,
        "gravity": 9.81,
        "lambda": 1020562,
        "mu": 22,
    },
    'Instationary': {'MaxTimeStepIts' : 2},
    'Mesh':  {'Filename': "/homes/students/weigl/workspace1/restflow/tmp/logoz.vtu"}}})

pprint.pprint(get_config(token))
results = apply(token)
print results