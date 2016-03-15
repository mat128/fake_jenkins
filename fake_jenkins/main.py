from flask import Flask

import fake_jenkins.api
import fake_jenkins.core

import sys

def main():
    app = Flask('fake_jenkins')
    core = fake_jenkins.core.Core()
    api = fake_jenkins.api.Api(core)
    api.hook_to(app)
    app.run(host=sys.argv[1],
            port=sys.argv[2])
