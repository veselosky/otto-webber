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
        ['build-essential', 'curl', 'git', 'python-dev', 'python-pip', 'python-virtualenv',
         'screen', 'tree', 'vim-nox'
        ],
    'WEBSERVER':
        ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom',
         'libapache2-mod-fcgid', 'libapache2-mod-wsgi',
         'mysql-client-5.1',
         'python-mysqldb',
         'libjpeg-progs', 'optipng', # image optimization tools for html5boilerplate build
        ],
    'PHP':
        ['php5-cli', 'php5-cgi', 'php5-adodb', 'php5-gd', 'php5-imagick',
         'php5-mysql', 'php5-suhosin', 'php-pear',
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
    SERVER_PACKAGES = PACKAGES['ANYSERVER'] + PACKAGES[servertype.upper()]
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -qy install '
        + ' '.join(SERVER_PACKAGES)
        )
    # But until we can configure passwd beforehand, we'll do it after.
    if 'mysql-server-5.1' in SERVER_PACKAGES:
        try:
            mysqlpassword = mysqlpassword or env.mysql.password
        except AttributeError:
            pass
        if mysqlpassword:
            # Note: If the password has already been set, this will fail, hence
            # the "warn only".
            with settings(warn_only=True):
                run('mysqladmin -u root password "%s"' % mysqlpassword)

    # install some python tools at the global level. Because I said so.
    sudo('pip install fabric sphinx')


def install_otto(force_update=False):
    """Install (or upgrade) the otto-webber code on a server.

    Because installing pip requirements can be slow and painful, it is not
    done automatically. Use force_update=True if you need to install or
    upgrade dependencies.
    """
    # Check out otto from a git repo onto the server. Use your own fork if you
    # want.
    otto_repo = env.get('otto_repo', 'https://github.com/veselosky/otto-webber.git')
    _ensure_git_updated(env['ottohome'], otto_repo, use_sudo=True)

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
def new_site(domain):
    """Create a new web site for the named user."""
    pass


def remote_deploy(name, repo, branch='master'):
    """Deploy a site from a git repo."""
    # Ensure latest otto code is on server.
    install_otto()

    # ensure home dir is prepared for otto
    setmeup()
    install_path = '~/otto-webber/' + name

    # TODO Disable crontab on server to prevent run with half-deployed code,
    # and to ensure if crontab is removed from new deployment the old one will
    # no longer be running.

    # check out the repo
    _ensure_git_updated(install_path, repo, branch)

    # Run the local_deploy task for the fresh repo
    with cd(env['ottohome']):
        run('fab local_deploy ' + install_path)


def local_deploy(dir):
    """Deploy a site on the local system.

    The remote_deploy task calls local_deploy on the server, to run python
    code on the server itself. The `dir` argument is where the repo has been
    checked out.
    """
    pass


# TODO Task to install Wordpress for a named user.

def test_remotes():
    """Test how fab works"""
    run('ls ~/bin')

##############################################################################
# UTILITY FUNCTIONS
##############################################################################

def _ensure_git_updated(target,repo,branch='master',use_sudo=False):
    """Ensure that a directory contains an up-to-date git clone.

    `target` is the directory where the clone should live
    `repo` is the git URL to clone if needed
    `branch` is the branch to check out. Default 'master'.
    `use_sudo` if True, git operations will be performed as superuser.
    """
    action = sudo if use_sudo else run
    if remotefile.exists(target+'/.git', verbose=env['verbose']):
        with cd(target):
            action('git fetch && git checkout %s' % branch)
    else:
        action('mkdir -p %s' % target)
        action('git clone %s %s' % (repo, target))
        with cd(target):
            action('git checkout %s' % branch)

