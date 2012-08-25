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


# TODO 0.4 install_etc must be called from post-receive hook. Changes?
def install_etc():
    """Install files from the current build's etc/ into /etc/

    Also remove stale links made by old builds. Used by deploy and rollback tasks."""
    site_dir = paths.site_dir()
    current = '%s/current' % site_dir
    etclinks = '%s/.etclinks-created' % site_dir

    # Install the newly deployed etc/ files. Record the links created so we can check
    # them later.
    with cd(current):
        sudo("""find etc -type d -print0 | xargs -0 -I '{}' mkdir -p '/{}'
        find etc -type f -print0 | xargs -0 -I '{}' ln -sf '%s/{}' '/{}'
        """ % current)
        with hide('stdout'):
            run('find etc -type f >> %s' % etclinks)

    # Check that all the links we have created still resolve (inluding links
    # from previous builds)
    if remotefile.exists(etclinks):
        # readlink -e returns true even if the thing is not a link!
        sudo("""for item in `sort %s | uniq`; do
        readlink -e /$item || rm /$item
        done
        """ % etclinks)

