"""Fabric tasks to automate my webserver infrastructure."""

from fabric.api import *
import fabric.contrib.files as remotefile

# TODO boto tasks to bring EC2 servers up and down
# TODO Configure an FTP Server.
# TODO Implement disk quotas for users

# 1. Assume Ubuntu 10.10 server base
PACKAGES = {
    'ANYSERVER':
        ['curl', 'git', 'screen', 'tree', 'vim-nox'],
    'WEBSERVER':
        ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom', 'libapache2-mod-fcgid',
         'mysql-client-5.1',
         'php5-cli', 'php5-cgi', 'php5-adodb', 'php5-gd', 'php5-imagick', 'php5-mysql', 'php5-suhosin', 'php-pear',
         'python-mysqldb',
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

    # Check out otto from a git repo onto the server. Use your own fork if you
    # want.
    otto_repo = env.get('otto_repo', 'https://github.com/veselosky/otto-webber.git')
    if remotefile.exists('/usr/local/share/otto-webber', verbose=True):
        with cd('/usr/local/share/otto-webber'):
            sudo('git pull')
    else:
        sudo('mkdir -p /usr/local/share')
        with cd('/usr/local/share'):
            sudo('git clone %s' % otto_repo)

# TODO Create & install /usr/local/sbin/adduser.local to customize user on creation.
def new_user(username):
    """Create a new user account."""
    sudo('/usr/sbin/adduser --conf /usr/local/share/otto-webber/server/adduser.conf %s' % username)

# TODO Task to set up new Apache VirtualHost for a named user.
# TODO Task to install Wordpress for a named user.