"""Fabric tasks to automate my webserver infrastructure."""

from fabric.api import env, local, task
import otto.web as web

env['verbose'] = True
env['otto.web.site'] = 'example.com'
env['otto.web.build_dir'] = './build'

@task
def build():
    """create a fake build to test with"""
    local('cp -a example.com build')
