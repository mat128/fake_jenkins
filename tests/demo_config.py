from fake_jenkins.core import Job, BuildParameter

FAKE_JENKINS_JOBS = {
    'demoJob': Job(name='demoJob',
                   auth_token='token',
                   parameters=[BuildParameter(name='hello',
                                              default_value='')])
}
