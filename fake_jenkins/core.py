class Core(object):
    def __init__(self):
        self.jobs = {}

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
