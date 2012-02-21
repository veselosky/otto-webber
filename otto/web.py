# encoding: UTF-8
"""Web deployment tasks for fabric.

These tasks are meant to be run as the "deployer". The deployer is a remote
user who:

* has certain sudo privileges (FIXME document which privileges),
* has write permission to deployment directory (env['otto.web.site_root']),
* is *not* the same user that your web server runs as (i.e. not www-data).

Set the following keys in your `env` to configure otto.web:

`otto.web.build_dir`
    *Required.* The local directory where your build task assembles the files to be
    uploaded.

`otto.web.site`
    *Required.* The domain name of the site Otto will be manipulating. This
    name is used to construct several paths on the remote server.

.. TODO:

    Document optional keys for constructing `site_dir`.
"""

from datetime import datetime
from fabric.api import  abort, cd, env, hide, lcd, local, put, require, run, sudo, task
from fabric import colors
import fabric.contrib.files as remotefile
import os.path
import os

DEFAULT_CONFIG = {
    'otto.web.prefix': '/usr/local',
    'otto.web.site_root': 'share/apache2/sites', # relative to prefix
    'otto.web.site_dir': '%(otto.web.prefix)s/%(otto.web.site_root)s/%(otto.web.site)s',
    }
for k, v in DEFAULT_CONFIG.iteritems():
    env.setdefault(k, v)

def _site_dir():
    """calculate the site directory"""
    require('otto.web.site', 'otto.web.site_root', 'otto.web.site_dir')
    site_dir = env['otto.web.site_dir'] % env
    if not site_dir.startswith('/'):
        abort('Site directory is not absolute: "%s"' % site_dir)
    return site_dir

@task
def setup():
    """Prepare target directories on server."""
    if env['otto.web.site_root'].startswith('/'):
        site_root = env['otto.web.site_root']
    else:
        site_root = '%(otto.web.prefix)s/%(otto.web.site_root)s' % env
    sudo('mkdir -p %s' % site_root)
    sudo('chown %s. %s' % (env['user'], site_root))


@task
def stage():
    """Upload site content to web server."""
    require('otto.web.build_dir')
    site_dir = _site_dir()
    deploy_ts = env['otto.web.deploy_ts'] = datetime.utcnow().isoformat()

    # Rename the local build dir to match to deploy_ts
    # Must remove trailing slash or os.path.dirname(x) returns x!
    build_dir = env['otto.web.build_dir'].rstrip(os.sep)
    localdir, basename = os.path.split(build_dir)
    with lcd(localdir):
        local('mv %s %s' % (basename, deploy_ts))
    tarfile = '%s.tar.gz' % deploy_ts
    local('tar -czf %s -C %s %s' % (tarfile, localdir, deploy_ts))

    # Upload the content to the server.
    run('mkdir -p %s' % site_dir)
    put(tarfile, site_dir)
    with cd(site_dir):
        run('tar --force-local -xzf %s' % tarfile)
        run("ln -sfn %s staged" % deploy_ts)
        run('rm %s' % tarfile)


@task
def deploy():
    """Make your staged site content "live"."""
    # TODO Support deployment of named builds by passing name arg.
    site_dir = _site_dir()
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

@task
def rollback():
    """Undo deployment, roll back to the previous deploy."""
    site_dir = _site_dir()
    if not remotefile.exists(site_dir + '/previous'):
        abort("No previous deployment to roll back to!")
    with cd(site_dir):
        run("""
            ln -sfn `readlink current` rolledback
            ln -sfn `readlink previous` current
        """)

@task
def cleanup():
    """Remove old unused deployments from server."""
    # TODO Smarter code so that any build that has a symlink is preserved.
    site_dir = _site_dir()
    with cd(site_dir):
        run("""
        current=`readlink current`
        previous=`readlink previous`
        staged=`readlink staged`
        for dir in `ls`; do
            [ $dir != "$current" ] && [ $dir != "$staged" ] && [ $dir != "$previous" ] && [ $dir != "current" ] && [ $dir != "staged" ] && [ $dir != "previous" ] && rm -rf $dir
        done
        echo "Cleaned old deployments."
        """)
clean_server = cleanup # backward compat

@task
def list():
    """List deployments available at the server"""
    site_dir = _site_dir()
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
def reload_apache():
    """Force apache to reload its configuration."""
    sudo('/etc/init.d/apache2 reload')

@task
def install_vhost():
    """Install apache support for the virtual host."""
    require('otto.web.site')
    site_dir = _site_dir()
    site = env['otto.web.site']

    vhost_path = "%s/current/etc/apache2/vhost.d/%s" % (site_dir, site)
    dest = '/etc/apache2/sites-available/'
    sudo("cp %s %s" % (vhost_path, dest))
    sudo("a2ensite %s" % site)
    reload_apache()

@task
def remove_vhost(purge=None):
    """Remove apache support for the virtual host."""
    sudo("a2dissite %s" % env['otto.web.site'])
    reload_apache()
    if purge != None:
        run('rm /etc/apache2/sites-available/%s' % env['otto.web.site'])
    # ¿Physically remove the conf from sites-available?


