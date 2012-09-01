# encoding: UTF-8
"""Namespace for generic server stuff."""

from fabric.api import cd, env, hide, run, sudo
import fabric.contrib.files as remotefile
from otto.util import paths

# TODO 0.4 expand `setup` to install git hooks.
def setup():
    """Prepare target directories on server."""
    sudo('mkdir -p %s' % env['otto.home'])
    sudo('chown -R %(user)s. %(otto.home)s' % env)
    run('mkdir -p %s' % paths.hooks())
    run('mkdir -p %s' % paths.repos())
    run('mkdir -p %s' % paths.sites())
    run('mkdir -p %s' % paths.virtualenvs())
    run('mkdir -p %s' % paths.workspace())


def service(name, action):
    """Run the service script on the server to start|stop|restart services"""
    sudo('service %s %s' % (name, action))

