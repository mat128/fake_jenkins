import random
import time

import os
import unittest

import subprocess

import sys

import requests
from hamcrest import assert_that
from hamcrest import is_


class EntrypointTest(unittest.TestCase):
    def setUp(self):
        self.port = random.randrange(10000, 20000)
        self.process = subprocess.Popen([
            os.path.join(os.path.dirname(sys.executable),
                         'fake_jenkins'),
            '0.0.0.0',
            str(self.port)
        ])

    def tearDown(self):
        self.process.terminate()

    def test_entry_point(self):
        for i in xrange(30):
            try:
                result = requests.get('http://127.0.0.1:{0}/'.format(self.port))
                assert_that(result.status_code, is_(404))
                break
            except Exception:
                time.sleep(1)

        result = requests.get('http://127.0.0.1:{0}/'.format(self.port))
        assert_that(result.status_code, is_(404))
