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

class Core(object):
    def __init__(self, jobs=None):
        self.jobs = jobs or {}

    def create_job(self, name, auth_token=None, parameters=None):
        self.jobs[name] = Job(name=name, auth_token=auth_token, parameters=parameters)

    def get_job(self, name):
        try:
            return self.jobs[name]
        except KeyError:
            raise JobNotFound(name)


class Job(object):
    def __init__(self, name, auth_token, parameters=None):
        self.name = name
        self.auth_token = auth_token
        if parameters is None:
            parameters = []
        self.parameters = parameters
        self.next_build_number = 1
        self.builds = {}

    def create_build(self, **kwargs):
        build_id = self.next_build_number

        params = {}
        for parameter in self.parameters:
            params[parameter.name] = kwargs.get(parameter.name, parameter.default_value)

        new_build = Build(build_id, parameters=params)
        self.builds[build_id] = new_build
        self.next_build_number += 1

        return new_build

    def get_build(self, build_number):
        try:
            return self.builds[build_number]
        except KeyError:
            raise BuildNotFound()

class Build(object):
    def __init__(self, number, parameters=None):
        if parameters is None:
            parameters = {}
        self.number = number
        self.parameters = parameters


class BuildParameter(object):
    def __init__(self, name, default_value):
        self.name = name
        self.default_value = default_value


class FakeJenkinsError(Exception):
    pass


class MissingResource(FakeJenkinsError):
    pass


class JobNotFound(MissingResource):
    pass


class BuildNotFound(MissingResource):
    pass
