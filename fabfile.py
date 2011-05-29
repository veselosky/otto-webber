"""Fabric tasks to automate my webserver infrastructure."""

from fabric.api import *
import fabric.contrib.files as remotefile

env['ottohome'] = '/usr/local/share/otto-webber'
env['verbose'] = False

# TODO boto tasks to bring EC2 servers up and down
# TODO Configure an FTP Server.
# TODO Implement disk quotas for users

# 1. Assume Ubuntu 10.10 server base
PACKAGES = {
    'ANYSERVER':
        ['build-essential', 'curl', 'git', 'screen', 'tree', 'vim-nox'],
    'WEBSERVER':
        ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom', 'libapache2-mod-fcgid',
         'mysql-client-5.1',
         'php5-cli', 'php5-cgi', 'php5-adodb', 'php5-gd', 'php5-imagick', 'php5-mysql', 'php5-suhosin', 'php-pear',
         'python-mysqldb','python-virtualenv',
        ],
    'DATABASE':
        ['mysql-server-5.1', 'mysql-client-5.1'],
}
PACKAGES['FULLSTACK'] = PACKAGES['WEBSERVER'] + PACKAGES['DATABASE']

# TASKS

def setup_server(servertype="FULLSTACK", mysqlpassword=None):
    """Install and configure requisite system packages on a bare server."""
    sudo('apt-get -qq update')
    sudo('apt-get -qy upgrade')
    # Setting frontend to noninteractive prevents prompting for mysql server
    # root password. This means mysql server root password will be empty.
    # TODO Use debconf to set a mysql server root password.
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -qy install '
        + ' '.join(PACKAGES['ANYSERVER'] + PACKAGES[servertype.upper()])
        )
    # But until we can configure this beforehand, we'll do it after.
    if not mysqlpassword:
        try:
            mysqlpassword = env.mysql.password
        except AttributeError:
            pass
    if mysqlpassword:
        # Note: If the password has already been set, this will fail, hence
        # the "warn only".
        with settings(warn_only=True):
            run('mysqladmin -u root password "%s"' % mysqlpassword)
    install_otto()

def install_otto(force_update=False):
    """Install (or upgrade) the otto-webber code on a server.

    Because installing pip requirements can be slow and painful, it is not
    done automatically. Use force_update=True if you need to install or
    upgrade dependencies.
    """
    # Check out otto from a git repo onto the server. Use your own fork if you
    # want.
    otto_repo = env.get('otto_repo', 'https://github.com/veselosky/otto-webber.git')
    if remotefile.exists(env['ottohome'], verbose=env['verbose']):
        with cd(env['ottohome']):
            sudo('git pull')
    else:
        sudo('mkdir -p %s' % env['ottohome'])
        sudo('git clone %s %s' % (otto_repo, env['ottohome']))

    # Create a python virtualenv where we will install otto's dependencies.
    venv = env['ottohome']+'/pyvenv'
    if force_update or not remotefile.exists(venv, verbose=env['verbose']):
        sudo('virtualenv --no-site-packages --clear ' + venv)
        sudo('source %s/bin/activate; pip install -Ur %s' % (venv, env['ottohome']+'/requirements.pip') )


# TODO Create & install /usr/local/sbin/adduser.local to customize user on creation.
def new_user(username):
    """Create a new user account."""
    sudo('/usr/sbin/adduser --conf %s/server/adduser.conf %s' % (env['ottohome'], username))


def setupmeup():
    """Setup otto-webber for an existing user.

    For now, can only setup the user who is executing the command, but that's a bug.
    """
    run('mdkdir -p ~/otto-webber')


# TODO Task to set up new Apache VirtualHost for a named user.
# TODO Task to install Wordpress for a named user.