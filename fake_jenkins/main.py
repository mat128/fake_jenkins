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
