# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import functools

import flask

from fake_jenkins.core import MissingResource, BuildParameter


def exception_handler(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except MissingResource:
            flask.abort(404)

    return wrapper


class Api(object):
    def __init__(self, core):
        self.core = core

    def hook_to(self, server):
        self.app = server
        self.app.add_url_rule('/buildByToken/build', view_func=self.build, methods=['GET'])
        self.app.add_url_rule('/buildByToken/buildWithParameters', view_func=self.build_with_parameters, methods=['GET'])
        self.app.add_url_rule('/job/<job_name>', view_func=self.create_job, methods=['POST'])
        self.app.add_url_rule('/job/<job_name>/api/json', view_func=self.get_job, methods=['GET'])
        self.app.add_url_rule('/job/<job_name>/<build_number>/api/json', view_func=self.get_build, methods=['GET'])

    def create_job(self, job_name):
        params = {}
        request_data = flask.request.data
        if request_data == '':
            data = {}
        else:
            data = json.loads(flask.request.data)
        if data:
            if 'auth_token' in data:
                params['auth_token'] = data['auth_token']

            if 'parameters' in data:
                params['parameters'] = []
                for parameter in data['parameters']:
                    params['parameters'].append(BuildParameter(name=parameter['name'],
                                   default_value=parameter['default_value']))
        self.core.create_job(name=job_name, **params)
        return flask.make_response('', 201)

    @exception_handler
    def build_with_parameters(self):
        parameters = {k: v for k, v in flask.request.args.items()}

        job_name = parameters.pop('job')
        token = parameters.pop('token')
        job = self.core.get_job(job_name)

        if token == job.auth_token:
            if job.create_build(**parameters):
                return 'Scheduled.'
        else:
            return flask.make_response('Authentication required', 403)

    @exception_handler
    def build(self):
        job_name = flask.request.args.get('job')
        token = flask.request.args.get('token')
        job = self.core.get_job(job_name)
        if len(job.parameters) > 0:
            return flask.make_response('use buildWithParameters for this build', 400)

        if token == job.auth_token:
            if job.create_build():
                return 'Scheduled.'
        else:
            return flask.make_response('Authentication required', 403)

    @exception_handler
    def get_job(self, job_name):
        job = self.core.get_job(job_name)
        response = flask.make_response(json.dumps(job_to_api_dict(job)))
        response.headers['Content-Type'] = 'application/json'
        return response

    @exception_handler
    def get_build(self, job_name, build_number):
        job = self.core.get_job(job_name)
        build = job.get_build(build_number)
        response = flask.make_response(json.dumps(build_to_api_dict(build)))
        response.headers['Content-Type'] = 'application/json'
        return response


def job_to_api_dict(job):
    return {'name': job.name,
            'builds': [
                {'number': j.number,
                 'url': '{0}job/{1}/{2}/'.format(flask.request.url_root, job.name, j.number)}
                for j in job.builds.values()]}


def build_to_api_dict(build):
    return {
        'actions': [
            {'causes': [
                {'shortDescription': ''}]
            },
            {'parameters': [
                {'name': key,
                 'value': value}
                for (key, value) in build.parameters.items()]}
        ]
    }
