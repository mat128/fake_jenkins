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
import unittest

import flask
import mock
from fake_jenkins import api
from fake_jenkins.core import JobNotFound, BuildParameter, Job, Build, BuildNotFound
from hamcrest import assert_that, is_, has_entry, has_key, has_length, has_item, has_entries, equal_to, \
    contains_string, has_properties


class FakeJenkinsServerTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.client = self.app.test_client()
        self.core = mock.Mock()
        self.api = api.Api(self.core)
        self.api.hook_to(self.app)

    def test_build(self):
        job_mock = Job(name='myJob', auth_token='validToken')
        job_mock.create_build = mock.Mock()
        self.core.get_job.return_value = job_mock

        response = self.client.get('/buildByToken/build?job=myJob&token=validToken')
        assert_that(response.status_code, is_(200))
        assert_that(response.data, is_('Scheduled.'))

        self.core.get_job.assert_called_with('myJob')
        job_mock.create_build.assert_called_with()

    def test_build_invalid_token(self):
        self.core.get_job.return_value = Job(name='myJob', auth_token='validToken')

        response = self.client.get('/buildByToken/build?job=myJob&token=invalidToken')
        assert_that(response.status_code, is_(403))
        assert_that(response.data, is_('Authentication required'))

    def test_build_job_does_not_exist(self):
        self.core.get_job.side_effect = JobNotFound

        response = self.client.get('/buildByToken/build?job=missingJob&token=myToken')
        assert_that(response.status_code, is_(404))

    def test_build_job_with_parameters_requires_buildWithParameters(self):
        self.core.get_job.return_value = Job(name='myParamsJob',
                                             auth_token='validToken',
                                             parameters=[BuildParameter(name='param1', default_value='')])

        response = self.client.get('/buildByToken/build?job=myParamsJob&token=validToken')
        assert_that(response.status_code, is_(400))
        assert_that(response.data, contains_string('use buildWithParameters for this build'))

    def test_build_with_parameters(self):
        job_mock = mock.Mock()
        job_mock.name = 'myJob'
        job_mock.auth_token = 'validToken'
        job_mock.parameters = [BuildParameter(name='hello', default_value='')]
        self.core.get_job.return_value = job_mock

        response = self.client.get('/buildByToken/buildWithParameters?job=myJob&token=validToken&hello=you')
        assert_that(response.status_code, is_(200))
        assert_that(response.data, is_('Scheduled.'))

        job_mock.create_build.assert_called_with(hello='you')

    def test_build_with_parameters_invalid_token(self):
        self.core.get_job.return_value = Job(name='myJob',
                                             auth_token='validToken')
        response = self.client.get('/buildByToken/buildWithParameters?job=myJob&token=invalidToken')
        assert_that(response.status_code, is_(403))
        assert_that(response.data, is_('Authentication required'))

    def test_build_with_parameters_job_does_not_exist(self):
        self.core.get_job.side_effect = JobNotFound
        response = self.client.get('/buildByToken/buildWithParameters?job=missingJob&token=myToken')
        assert_that(response.status_code, is_(404))

    def test_get_job_without_builds(self):
        self.core.get_job.return_value = Job(name='myJob', auth_token=None)
        response = self.client.get('/job/myJob/api/json')
        assert_that(response.status_code, is_(200))
        assert_that(response.content_type, is_("application/json"))

        decoded_response = json.loads(response.data)

        assert_that(decoded_response, has_entry('name', 'myJob'))
        assert_that(decoded_response, has_key('builds'))
        assert_that(decoded_response['builds'], has_length(0))

    def test_get_job_does_not_exist(self):
        self.core.get_job.side_effect = JobNotFound
        response = self.client.get('/job/missingJob/api/json')
        assert_that(response.status_code, is_(404))

    def test_get_job_with_builds(self):
        job = Job(name='myJob', auth_token=None)
        job.create_build()
        self.core.get_job.return_value = job

        builds = json.loads(self.client.get('/job/myJob/api/json').data).get('builds')
        assert_that(builds, has_length(1))
        assert_that(builds, has_item(has_entries(number=equal_to(1), url=equal_to('http://localhost/job/myJob/1/'))))

    def test_create_job(self):
        response = self.client.post('/job/newJob')
        assert_that(response.status_code, is_(201))

        self.core.create_job.assert_called_with(name='newJob')

    def test_create_job_with_auth_token(self):
        response = self.client.post('/job/newJob', data=json.dumps({
            'auth_token': 'myToken'
        }))
        assert_that(response.status_code, is_(201))

        self.core.create_job.assert_called_with(name='newJob', auth_token='myToken')

    def test_create_job_with_parameters(self):
        response = self.client.post('/job/newJob', data=json.dumps({
            'parameters': [
                {'name': 'hello', 'default_value': 'world'},
            ]
        }))
        assert_that(response.status_code, is_(201))

        assert_that(self.core.create_job.called, is_(True))
        assert_that(self.core.create_job.call_args[1], has_entry('name', 'newJob'))
        assert_that(self.core.create_job.call_args[1], has_entry('parameters', has_length(1)))
        assert_that(self.core.create_job.call_args[1]['parameters'][0], has_properties(name='hello', default_value='world'))


    def test_get_build(self):
        job_mock = mock.Mock()
        job_mock.get_build.return_value = Build(1, parameters={'hello2': 'world2'})
        self.core.get_job.return_value = job_mock

        response = self.client.get('/job/{job}/{build}/api/json'.format(job='myJob', build=1))
        assert_that(response.status_code, is_(200))
        assert_that(response.content_type, is_("application/json"))

        decoded_response = json.loads(response.data)

        assert_that(decoded_response, has_entry('actions', has_item(has_entry('causes', has_item(has_key('shortDescription'))))))
        assert_that(decoded_response, has_entry('actions', has_item(has_entry('parameters', has_item(has_entry('name', 'hello2'))))))
        assert_that(decoded_response, has_entry('actions', has_item(has_entry('parameters', has_item(has_entry('value', 'world2'))))))

    def test_get_build_job_does_not_exist(self):
        self.core.get_job.side_effect = JobNotFound
        response = self.client.get('/job/missingJob/1/api/json')
        assert_that(response.status_code, is_(404))

    def test_get_build_job_exists_but_build_not_found(self):
        job_mock = mock.Mock()
        job_mock.get_build.side_effect = BuildNotFound
        self.core.get_job.return_value = job_mock
        response = self.client.get('/job/myJob/42/api/json')
        assert_that(response.status_code, is_(404))
