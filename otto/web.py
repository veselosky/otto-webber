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
__all__ = ['cleanup', 'deploy', 'golive', 'list', 'rollback']
from fabric.api import abort, cd, env, execute, local, prefix, require, run, sudo, task
import fabric.contrib.files as remotefile
import os.path

import otto.git as git
from otto.util import make_timestamp, paths
from otto.server import install_etc, service

#######################################################################
# Fab Tasks
#######################################################################
# FIXME Default target should be env[staging_branch] bidgaf
@task
def deploy(target=None):
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
    if target == None:
        target = env['otto.git.staging_branch']
        mods = git.local_modifications()
        if mods != None:
            abort("Local modifications! Specify a tag to deploy or check in your workspace.")

    tagname = "otto-" + make_timestamp()
    local('git tag -f %s %s' % (tagname, target))
    git.push()
    # Fuck it, I'll do the work here instead of in a hook.
    # Check out the tag into the workspace
    basename = os.path.basename(paths.project_dir())
    remote_repo = paths.repos(basename)
    workspace = paths.workspace(basename)
    git.clone_or_update(workspace, remote_repo)

    with cd(workspace):
        run('git reset --hard ' + tagname)

        # Ensure the virtualenv has been built
        checksum = run('md5sum requirements.txt | awk {print $1}')
        virtualenv_path = paths.virtualenvs(checksum)
        venv_activate = paths.virtualenvs(checksum, 'bin', 'activate')
        if not remotefile.exists(venv_activate):
            run('mkvirtualenv -r requirements.txt --system-site-packages ' + virtualenv_path)

        # Activate the virtualenv and run the build task
        with prefix('source ' + venv_activate):
            run('fab build')

        # rsync the built site into the site dir
        # install_etc
        # enable_vhost


@task
def rollback(to=None):
    """Undo deployment, roll back to the previous deploy."""
    if to == None:
        to = git.list_tags('otto-*')[1] # 2nd most recent
    deploy(to)


@task
def cleanup():
    """Remove old deployment tags (retains 3 most recent)."""
    tags = git.list_tags('otto-*')[3:]
    print 'TAGS: '.join(tags)
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
    """Remove the site from the web server's configuration"""
    require('otto.site', 'otto.httpserver')
    site = env['otto.site']
    server = env['otto.httpserver']
    enabled = '/etc/%s/sites-enabled/%s' % (server, site)
    if remotefile.exists(enabled):
        sudo('rm %s' % enabled)
    service(server, 'reload')

@task
def golive():
    """Push the built site to the web servers.

    Normally this will be called by Otto's git hooks, so there's no need to
    call it yourself. However, if you disable the git hooks for some reason, or
    need to push code live from your local machine, you could use this task.
    """
    # TODO 0.4 rsync files to the host
    execute(install_etc)
    execute(enable_site)

