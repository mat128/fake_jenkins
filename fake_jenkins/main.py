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

from flask import Flask

import fake_jenkins.api
import fake_jenkins.core

import sys

def main():
    app = Flask('fake_jenkins')
    app.config.from_envvar('FAKE_JENKINS_CONFIG_FILE', silent=True)

    core = fake_jenkins.core.Core(jobs=app.config.get('FAKE_JENKINS_JOBS'))
    api = fake_jenkins.api.Api(core)
    api.hook_to(app)
    app.run(host=sys.argv[1],
            port=int(sys.argv[2]),
            debug=True)
