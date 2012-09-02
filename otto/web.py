# encoding: UTF-8
"""Web deployment tasks for fabric.

These tasks are meant to be run as the "deployer". The deployer is a remote
user who:

* has certain sudo privileges (FIXME document which privileges),
* has write permission to deployment directory (env['otto.web.site_root']),
* is *not* the same user that your web server runs as (i.e. not www-data).

Set the following keys in your `env` to configure otto.web:

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

from fabric.api import  abort, cd, env, hide, local, prefix, require, run, sudo, task
from fabric import colors
import fabric.contrib.files as remotefile

import otto.git as git
from otto.util import make_timestamp, paths
from otto.server import setup, service

#######################################################################
# Utility Functions
#######################################################################
def _install_etc():
    """Install files from the current build's etc/ into /etc/

    Also remove stale links made by old builds. Used by deploy and rollback tasks."""
    current = paths.site_dir('current')
    etclinks = paths.site_dir('.etclinks-created')

    # Install the newly deployed etc/ files. Record the links created so we can check
    # them later.
    with cd(current):
        # Workaround: fabric 1.4.3 will execute this block even if the cd fails!
        run("[ `pwd` == '%s' ] && pwd" % current)

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
        readlink -e /$item || rm -f /$item
        done
        """ % etclinks)

#######################################################################
# Fab Tasks
#######################################################################
@task
def stage(target=None):
    """Upload site content to web server.

    When you run the stage task, Otto pushes your code to the server and then
    runs the `clean` and `build` tasks at the server to produce your web site
    files. The clean task is run to ensure files removed from the repository
    are also removed from the build. You are responsible for ensuring `clean`
    does the right thing!

    Otto then uses rsync to copy the content to a staging directory from which
    it can be deployed. If necessary, Otto will setup Otto on your server, and
    add the otto remote to your local repo.

    If no tag name is supplied as an argument, Otto will attempt to tag the
    HEAD of the current branch, or if you are operating with a detached HEAD
    (ouch!), the branch named in `env['otto.git.staging_branch']`. However,
    Otto will refuse to do so if you have modifications in your local
    workspace, as this could result in the remote build being different from
    the local build.
    """
    # Perform the server setup just in time 
    if not remotefile.exists(paths.repos()):
        setup()

    deploy_ts = make_timestamp()

    if target == None:
        target = local("git branch | grep '^\*' | awk '{print $2}'", capture=True)
        if not target:
            target = env['otto.git.staging_branch']
        mods = git.local_modifications()
        if mods != None:
            print colors.red('Local modifications! You may get unexpected results from your build.')
            abort(" Specify a tag to stage or check in your workspace.")

    tagname = "otto-" + deploy_ts
    local('git tag -f %s %s' % (tagname, target))
    git.push()

    # Check out the tag into the workspace
    basename = env['otto.site']
    remote_repo = paths.repos(basename)
    workspace = paths.workspace(basename)
    git.clone_or_update(workspace, remote_repo)

    with cd(workspace):
        run('git reset --hard ' + tagname)

        # Ensure the virtualenv has been built
        checksum = run("md5sum requirements.txt | awk '{print $1}'")
        virtualenv_path = paths.virtualenvs(checksum)
        venv_activate = paths.virtualenvs(checksum, 'bin', 'activate')
        if not remotefile.exists(venv_activate):
            run('virtualenv --system-site-packages ' + virtualenv_path)
            run('pip install -r requirements.txt -E ' + virtualenv_path)

        # Activate the virtualenv and run the build task
        build_dir = paths.workspace(env['otto.site'], env['otto.build_dir'])
        if not build_dir.endswith('/'):
            build_dir += '/'
        stage_dir = paths.site_dir(deploy_ts)
        with prefix('source ' + venv_activate):
            has_clean = run("fab --shortlist | grep '^clean$'")
            if has_clean.succeeded:
                run('fab clean')
            run('fab build')
        run('mkdir -p ' + stage_dir)
        run('rsync -a %s %s' % (build_dir, stage_dir))
        with cd(paths.site_dir()):
            run('ln -sfn %s staged' % deploy_ts)


@task
def deploy():
    """Make your staged site content "live"."""
    site_dir = paths.site_dir()
    if not remotefile.exists(site_dir + '/staged'):
        abort("No staged build to deploy! Use the stage task first.")

    # Update the "previous" and "current" links
    with cd(site_dir):
        run("""
        if [ -L current ] && [ `readlink current` != `readlink staged` ] ; then
            ln -sfn `readlink current` previous
        fi
        ln -sfn `readlink staged` current
        """)
    _install_etc()
    enable_site()


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
    _install_etc()
    enable_site()


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
        sudo('ln -sf %s %s' % (available, enabled))
    service(server, 'reload')

@task
def disable_site():
    """Add the site to the web server's configuration"""
    require('otto.site', 'otto.httpserver')
    site = env['otto.site']
    server = env['otto.httpserver']
    enabled = '/etc/%s/sites-enabled/%s' % (server, site)
    if remotefile.exists(enabled):
        sudo('rm  -f %s' % enabled)
    service(server, 'reload')

