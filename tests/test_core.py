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

import unittest

from fake_jenkins import core
from fake_jenkins.core import BuildParameter, JobNotFound, BuildNotFound, Job
from hamcrest import assert_that, is_, has_entry, has_length


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.core = core.Core()

    def test_core_can_take_jobs(self):
        c = core.Core(jobs={'myJob': Job('myJob', auth_token='yes')})
        job = c.get_job('myJob')
        assert_that(job.name, is_('myJob'))

    def test_job(self):
        self.core.create_job(name='test_job')

        job = self.core.get_job('test_job')

        assert_that(job.name, is_('test_job'))
        assert_that(job.auth_token, is_(None))

    def test_job_doesnt_exist(self):
        with self.assertRaises(JobNotFound):
            self.core.get_job('test_job')

    def test_job_with_token(self):
        self.core.create_job(name='test_job_with_token', auth_token='myToken')

        job = self.core.get_job('test_job_with_token')

        assert_that(job.name, is_('test_job_with_token'))
        assert_that(job.auth_token, is_('myToken'))

    def test_job_parameter(self):
        param = BuildParameter(name='test',
                               default_value='')

        assert_that(param.name, is_('test'))
        assert_that(param.default_value, is_(''))

    def test_build(self):
        self.core.create_job(name='test_job')
        job = self.core.get_job('test_job')

        assert_that(job.next_build_number, is_(1))

        build = job.create_build()
        assert_that(build.number, is_(1))
        assert_that(job.next_build_number, is_(2))

    def test_build_with_parameters(self):
        self.core.create_job(name='test_job', parameters=[BuildParameter(name='hello',
                                                                         default_value='')])
        job = self.core.get_job('test_job')

        build = job.create_build(hello='world')
        assert_that(build.number, is_(1))
        assert_that(build.parameters, has_length(1))
        assert_that(build.parameters, has_entry('hello', 'world'))

    def test_build_with_parameters_fallback_to_defaults(self):
        self.core.create_job(name='test_job', parameters=[BuildParameter(name='hello',
                                                                         default_value='')])
        job = self.core.get_job('test_job')

        build = job.create_build()
        assert_that(build.number, is_(1))
        assert_that(build.parameters, has_length(1))
        assert_that(build.parameters, has_entry('hello', ''))

    def test_build_with_parameters_extra_params_are_ignored(self):
        self.core.create_job(name='test_job', parameters=[BuildParameter(name='hello',
                                                                         default_value='')])
        job = self.core.get_job('test_job')

        build = job.create_build(test='yes')
        assert_that(build.number, is_(1))

        build = job.get_build(build.number)
        assert_that(build.parameters, has_length(1))
        assert_that(build.parameters, has_entry('hello', ''))

    def test_job_get_build(self):
        self.core.create_job(name='test_job')
        job = self.core.get_job('test_job')
        build = job.create_build()
        build_number = build.number

        new_build = job.get_build(build_number)

    def test_job_get_build_not_found(self):
        self.core.create_job(name='test_job')
        job = self.core.get_job('test_job')

        with self.assertRaises(BuildNotFound):
            job.get_build(42)
