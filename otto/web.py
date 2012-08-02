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
    uploaded.

`otto.site`
    *Required.* The domain name of the site Otto will be manipulating. This
    name is used to construct several paths on the remote server.

`otto.httpserver`
    *Optional.* Default="apache2". The name of your HTTP server. Used by
    `enable_vhost` and `disable_vhost` as the name of the service to restart,
    and the name of the directory to manipulate under `/etc/`.

"""

from datetime import datetime
from fabric.api import  abort, cd, env, hide, lcd, local, put, require, run, sudo, task
from fabric import colors
import fabric.contrib.files as remotefile
import os.path
import os
from otto.util import paths
from otto.server import service, install_etc

#######################################################################
# Fab Tasks
#######################################################################
# TODO 0.4 `stage` should merge to local staging branch, then push.
@task
def stage():
    """Upload site content to web server.

    If the package contains a requirements.txt file, Otto will also install a
    Python virtualenv into the staged directory and install the requirements.
    """
    require('otto.build_dir')
    site_dir = paths.site_dir()
    # Changed from isodate() because colons in the path crashed virtualenv, and
    # are a generally bad idea anyway.
    deploy_ts = env['otto.deploy_ts'] = datetime.utcnow().strftime('%Y%m%d-%H%M%S.%f')

    # Rename the local build dir to match to deploy_ts
    # Must remove trailing slash or os.path.dirname(x) returns x!
    build_dir = env['otto.build_dir'].rstrip(os.sep)
    localdir, basename = os.path.split(build_dir)
    with lcd(localdir):
        local('mv %s %s' % (basename, deploy_ts))
        tarfile = '%s.tar.gz' % deploy_ts
        local('tar -czf %s %s' % (tarfile, deploy_ts))

    # Upload the content to the server.
    run('mkdir -p %s' % site_dir)
    put(localdir+'/'+tarfile, site_dir)
    with cd(site_dir):
        run('tar --force-local -xzf %s' % tarfile)
        run("ln -sfn %s staged" % deploy_ts)
        run('rm %s' % tarfile)
        # TODO If a requirements file was installed, make the staged dir a virtualenv
        # and install the requirements.

        # NOTE This cannot be done at the build
        # stage because the installed packages might be system-specific.
        # FIXME Using test on remote causes fabric to throw an error because its return status is false.
#        run('[ -f "%(otto.deploy_ts)s/%(otto.requirements_file)s" ] && \
#            virtualenv --system-site-packages "%(otto.deploy_ts)s/" && \
#            pip install -q -E "%(otto.deploy_ts)s" -r "%(otto.deploy_ts)s/%(otto.requirements_file)s"' % env)


# TODO 0.4 `deploy` should merge to local deploy branch, then push.
@task
def deploy():
    """Make your staged site content "live"."""
    # TODO Support deployment of named builds by passing name arg.
    site_dir = paths.site_dir()
    if not remotefile.exists(site_dir + '/staged'):
        abort("No staged build to deploy! Use the stage task first.")

    # Update the "previous" and "current" links
    with cd(site_dir):
        run("""
        if [ -L current ]; then
            ln -sfn `readlink current` previous
        fi
        """)
        run("ln -sfn `readlink staged` current && rm staged")
    install_etc()


# TODO 0.4 `rollback` should rollback the local deploy branch & push
@task
def rollback():
    """Undo deployment, roll back to the previous deploy."""
    site_dir = paths.site_dir()
    if not remotefile.exists(site_dir + '/previous'):
        abort("No previous deployment to roll back to!")
    with cd(site_dir):
        run("""
            ln -sfn `readlink current` rolledback
            ln -sfn `readlink previous` current
        """)
    install_etc()


@task
def cleanup():
    """Remove old unused deployments from server.

    Any build that has a symbolic link in this directory pointing to it will be preserved.
    Also trims the database of /etc/ links created down to ones that currently exist."""
    site_dir = paths.site_dir()
    etclinks = '%s/.etclinks-created' % site_dir

    with cd(site_dir):
        run("""find . -maxdepth 1 -type l -print0 | xargs -0 -n 1 readlink > ../keeplist
        for dir in `ls | grep -f ../keeplist -v`; do
            [ ! -L $dir ] && rm -rf $dir
        done
        rm ../keeplist
        for file in `sort %s | uniq`; do
            [ -e /$file ] && echo $file >> %s
        done
        echo "Cleaned old deployments."
        """ % (etclinks, etclinks))
clean_server = cleanup # backward compat

@task
def list():
    """List deployments available at the server"""
    site_dir = paths.site_dir()
    with cd(site_dir):
        with hide('running', 'stdout'):
            current = run('[ -e current ] && readlink current || echo None')
            previous = run('[ -e previous ] && readlink previous || echo None')
            staged = run('[ -e staged ] && readlink staged || echo None')
            available = run('ls -d [0123456789]* | sort')

        print colors.green("Current: %s" % current)
        print colors.yellow("Staged: %s" % staged)
        print colors.red("Previous: %s" % previous)
        print "Available:\n%s" % available


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

