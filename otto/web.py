# encoding: UTF-8
"""Web deployment tasks for fabric.

These tasks are meant to be run as the "deployer". The deployer is a remote
user who:

* has certain sudo privileges (FIXME document which privileges),
* has write permission to deployment directory (env['otto.site_root']),
* is *not* the same user that your web server runs as (i.e. not www-data).

Set the following keys in your `env` to configure otto:

`otto.build_dir`
    *Required.* The local directory where your build task assembles the files to be
    uploaded. MUST be relative to the project root (where the fabfile lives).

`otto.site`
    *Required.* The domain name of the site Otto will be manipulating. This
    name is used to construct several paths on the remote server.

`otto.httpserver`
    *Optional.* Default="apache2". The name of your HTTP server. Used by
    `enable_vhost` and `disable_vhost` as the name of the service to restart,
    and the name of the directory to manipulate under `/etc/`.

"""
from fabric.api import  env, local, require, sudo, task
import fabric.contrib.files as remotefile

import otto.git as git
from otto.util import make_timestamp
from otto.server import service

# Notes on post-receive hook:
# build()
# rsync to deploy dir
# install_etc()

#######################################################################
# Fab Tasks
#######################################################################
# FIXME Default target should be env[staging_branch] bidgaf
@task
def deploy(target='master'):
    """Make your staged site content "live".

    Otto creates a new tag on the staging branch (master by default) using the
    current date-time in this format: ("otto-YYYYMMDD-hhmmss"). If you supply a
    tag/branch/hash as an argument, Otto will tag the hash you specified.
    Otherwise, Otto will check for local changes (using `git status`) and if it
    finds none, will tag HEAD.

    After creating the tag, Otto will push it to the remote otto repo.

    The git hook on the remote otto repo will check out the tag and run the
    build task to generate output to the staging area. It will then rsync the
    built files from the staging area to the deployment area.
    """
    # FIXME Produce reasonable output if local modifications on deploy
    mods = git.local_modifications()
    if mods != None:
        raise Exception("Local modifications!")

    tagname = "otto-" + make_timestamp()
    git.tag(tagname, target, force=True)
    local('git tag -f %s %s' % (tagname, target))
    git.push()


@task
def rollback(to=None):
    """Undo deployment, roll back to the previous deploy."""
    if to == None:
        to = git.tag_list('otto-*')[1] # 2nd most recent
    deploy(to)


@task
def cleanup():
    """Remove old deployment tags (retains 3 most recent)."""
    tags = git.tag_list('otto-*')[3:]
    if tags:
        local('git tag -d ' + ' '.join(tags))


@task
def list():
    """List deployment tags available"""
    local('git tag -l otto-* | sort -r')


@task
def enable_site():
    """Add the site to the web server's configuration"""
    require('otto.site', 'otto.httpserver')
    site = env['otto.site']
    server = env['otto.httpserver']
    available = '/etc/%s/sites-available/%s' % (server, site)
    enabled = '/etc/%s/sites-enabled/%s' % (server, site)
    if remotefile.exists(available):
        sudo('ln -s %s %s' % (available, enabled))
    service(server, 'reload')


@task
def disable_site():
    """Add the site to the web server's configuration"""
    require('otto.site', 'otto.httpserver')
    site = env['otto.site']
    server = env['otto.httpserver']
    enabled = '/etc/%s/sites-enabled/%s' % (server, site)
    if remotefile.exists(enabled):
        sudo('rm %s' % enabled)
    service(server, 'reload')

